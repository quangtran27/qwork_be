from uuid import UUID

from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.decorators import api_view
from rest_framework.response import Response

from applications.serialziers import ApplicationDetailSerializer
from authentication.utils import Util
from candidates.models import CandidateProfile
from candidates.serializers import CandidateProfileSerializer
from jobs.models import Job
from jobs.serializers import JobDetailSerializer
from recruiters.models import RecruiterProfile
from recruiters.serializers import RecruiterProfileSerializer
from users.models import User
from users.serializers import UserInfoSerializer, UserSerializer
from utils.api_response import make_response
from utils.sample_data import SERVER_ERROR_RESPONSE
from utils.token import check_auth
from utils.validators import is_valid_uuid


@api_view(['POST'])
def register(request):
  data = request.data

  # Validate
  if data['role'] not in ['recruiter', 'candidate']:
    return make_response(False, 400, 'Loại tài khoản không hợp lệ!')
  if len(User.objects.filter(phone=data['phone'])) > 0:
    return make_response(False, 400, 'Số điện thoại đã được sử dụng!')
  if len(User.objects.filter(email=data['email'])) > 0:
    return make_response(False, 400, 'Email đã được sử dụng!')

  password = data.get('password', '')
  data['password'] = make_password(password)
  user_serializer = UserSerializer(data=data)
  if user_serializer.is_valid():
    try:
      user: User = user_serializer.save()
      user.is_active = False
      user.save()

      origin = request.headers['Origin']
      token = PasswordResetTokenGenerator().make_token(user)
      email_data = {
        'to_email': user.email,
        'email_subject': 'Kích hoạt tài khoản QWork',
        'email_body': f'Xin chào {user.name},\nBạn hãy sử dụng đường link này để kích hoạt tài khoản của bạn trên QWork: {origin}/active/{user.email}/{token}'
      }
      Util.send_email(email_data)

      if user.role == 'recruiter':
        profile = RecruiterProfile(
          user=user, 
          avatar=None, 
          name=user.name, 
          description='', 
          phone=user.phone, 
          email=user.email, 
          address='Cập nhật địa chỉ'
        )
      else:
        profile = CandidateProfile(
          user=user, 
          avatar=None, 
          name=user.name, 
          phone=user.phone, 
          description='', 
          address='Cập nhật địa chỉ',
          position='Cập nhật vị trí trong công việc',
          gender='male',
          birth_day='2000-01-01',
          email=user.email
        )
        
      profile.save()

      user.password = ''
      return make_response(True, 201, 'Đăng ký tài khoản thành công!', UserSerializer(user).data)
    except Exception as e:
      print('Error saving user from register: ', e)
      return SERVER_ERROR_RESPONSE
  else:
    return make_response(False, 400, 'Thông tin không hợp lệ, vui lòng kiểm tra lại')

@api_view(['GET'])
def get_user_profile(request, id) -> Response:
  if not is_valid_uuid(id):
    return make_response(False, 404, 'Hồ sơ không tồn tại')
  
  try:
    user = User.objects.get(id=UUID(id))
  except User.DoesNotExist:
    return make_response(False, 404, 'Hồ sơ không tồn tại')
  
  if user.role == 'recruiter':
    profile = user.recruiterprofile
    data = RecruiterProfileSerializer(profile).data
    data['type'] = 'recruiter'
    return make_response(True, 200, data=data)
  elif user.role == 'candidate':
    profile = user.candidateprofile
    data=CandidateProfileSerializer(profile).data
    data['type'] = 'candidate'
    return make_response(True, 200, data=data)

  return make_response(False, 403, 'Quyền không hợp lệ')

@api_view(['GET'])
def get_user_applications(request, id) -> Response:
  if not is_valid_uuid(id):
    return make_response(False, 404, 'Hồ sơ không tồn tại')
  
  [is_authenticated, decoded_token, messagge] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, messagge)

  try:
    user = User.objects.get(id=UUID(id))
  except User.DoesNotExist:
    return make_response(False, 404, 'Hồ sơ không tồn tại')

  if not user.role == 'candidate' or str(decoded_token['user_id']) != str(user.id):
    return make_response(False, 403, 'Bạn không có quyền tạo mới đơn ứng tuyển')

  status = request.query_params.get('status')

  applications = user.application_set.all()

  if status is not None and status != '0':
    applications = applications.filter(status=status)

  return make_response(True, 200, '', ApplicationDetailSerializer(applications, many=True).data)

@api_view(['GET', 'PATCH'])
def get_or_update_user_saved_jobs(request, id):
  if not is_valid_uuid(id):
    return make_response(False, 404, 'Người dùng không tồn tại')
  try:
    user = User.objects.get(id=id)
  except User.DoesNotExist:
    return make_response(False, 404, 'Hồ sơ người dùng không tồn tại')
  
  if not user.role == 'candidate':
    return make_response(False, 404, 'Nhà tuyển dụng không có quyền truy cập')
  
  if request.method == 'GET':
    return make_response(True, 200, '', JobDetailSerializer(user.candidateprofile.saved_jobs, many=True).data)
  
  try:
    job = Job.objects.get(id=request.data.get('job_id'))
  except:
    return make_response(False, 404, 'Công việc không tồn tại')

  action = request.data.get('action', 'add')
  if action not in ['add', 'remove']:
    return make_response(False, 200, 'Hành động không xác định')

  profile: CandidateProfile = user.candidateprofile
  
  if action == 'add':
    profile.saved_jobs.add(job)
    profile.save()
    return make_response(True, 200, 'Lưu tin tuyển dụng thành công', JobDetailSerializer(profile.saved_jobs, many=True).data)
  else: # remove
    profile.saved_jobs.remove(job)
    profile.save()
    return make_response(True, 200, 'Bỏ lưu tin tuyển dụng thành công', JobDetailSerializer(profile.saved_jobs, many=True).data)
  
@api_view(['PATCH'])
def update_user_info(request, id):
  if not is_valid_uuid(id):
    return make_response(False, 404, 'Người dùng không tồn tại')

  [is_authenticated, decoded_token, messagge] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, messagge)
  
  try:
    user = User.objects.get(id=id)
  except User.DoesNotExist:
    return make_response(False, 404, 'Hồ sơ người dùng không tồn tại')
  
  if decoded_token['user_id'] != str(user.id):
    return make_response(False, 403, 'Tài khoản không có quyền cập nhật thông tin người dùng')

  serializer = UserInfoSerializer(user, data=request.data, partial=True)
  if serializer.is_valid():
    user = serializer.save()
    user.password = ''
    return make_response(True, 200, 'Cập nhật hành công!', UserSerializer(user).data)
  else:
    message = 'Thông tin không hợp lệ, vui lòng kiểm tra lại'
    if serializer._errors['phone'] is not None:
      message = 'Số điện thoại đã được sử dụng'
    return make_response(False, 400, message)

@api_view(['PATCH'])
def active_user(request, email, token):
  try:
    user = User.objects.get(email=email)
    if user.is_active:
      return make_response(False, 400, 'Tài khoản đã được kích hoạt trước đó')
    
    if PasswordResetTokenGenerator().check_token(user, token):
      user.is_active = True
      user.save()
      return make_response(True, 200, 'Kích hoạt tài khoản thành công!')
    return make_response(False, 400, 'Mã kích hoạt không hợp lệ')

  except User.DoesNotExist:
    return make_response(False, 404, 'Hồ sơ người dùng không tồn tại')

@api_view()
def get_user_application_cvs(request, id):
  if not is_valid_uuid(id):
    return make_response(False, 404, 'Người dùng không tồn tại')

  [is_authenticated, decoded_token, messagge] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, messagge)
  
  try:
    user = User.objects.get(id=id)
  except User.DoesNotExist:
    return make_response(False, 404, 'Hồ sơ người dùng không tồn tại')
  
  if str(user.id) != decoded_token['user_id']:
    return make_response(False, 403, 'Bạn không có quyền truy cập')

  applications = user.application_set.all()
  cvs = []
  for application in applications:
    cvs.append(application.cv)

  return make_response(True, 200, data=cvs)
  
@api_view(['GET'])
def send_email_active(request, email):
  try:
    user = User.objects.get(email=email)
  except:
    return make_response(False, 404, 'Tài khoản không tồn tại')

  if user.is_active:
    return make_response(False, 400, 'Tài khoản đã được kích hoạt trước đó')

  origin = request.headers['Origin']
  token = PasswordResetTokenGenerator().make_token(user)
  email_data = {
    'to_email': user.email,
    'email_subject': 'Kích hoạt tài khoản QWork',
    'email_body': f'Xin chào {user.name},\nBạn hãy sử dụng đường link này để kích hoạt tài khoản của bạn trên QWork: {origin}/active/{user.email}/{token}'
  }
  try:
    Util.send_email(email_data)
    return make_response(True, 200, f'Đã gửi email kích hoạt tài khoản đến {user.email}')
  except:
    return make_response(False, 200, 'Đã xảy ra lỗi')
