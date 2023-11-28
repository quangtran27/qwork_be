from uuid import UUID

from django.contrib.auth.hashers import make_password
from requests import Request
from rest_framework.decorators import api_view
from rest_framework.response import Response

from applications.serialziers import ApplicationDetailSerializer
from candidates.models import CandidateProfile
from candidates.serializers import CandidateProfileSerializer
from recruiters.models import RecruiterProfile
from recruiters.serializers import RecruiterProfileSerializer
from users.models import User
from users.serializers import UserSerializer
from utils.api_response import make_response
from utils.sample_data import SERVER_ERROR_RESPONSE
from utils.token import check_auth, check_permissions
from utils.validators import is_valid_uuid


@api_view(['POST'])
def register(request):
  data = request.data

  # Validations
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

      if user.role == 'recruiter':
        profile = RecruiterProfile(
          user=user, 
          avatar=None, 
          name=user.name, 
          description='Cập nhật mô tả', 
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
          description='Cập nhật mô tả', 
          address='Cập nhật địa chỉ',
          position='Cập nhật vị trí trong công việc',
          gender='male',
          birth_day='2000-01-01',
          email=user.email
        )
        
      profile.save()

      user.password = ''
      return make_response(True, 201, 'Đăng ký thành công!', UserSerializer(user).data)
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

  applications = user.application_set.all()

  return make_response(True, 200, '', ApplicationDetailSerializer(applications, many=True).data)