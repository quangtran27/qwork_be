import os
from datetime import datetime

from firebase_admin import storage
from requests import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from candidates.models import CandidateProfile
from candidates.serializers import CandidateProfileSerializer
from users.models import User
from utils.api_response import make_response
from utils.firebase import delete_file
from utils.sample_data import SERVER_ERROR_RESPONSE
from utils.token import check_auth, decode_token


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_candidate_profile(request) -> Response:
  authorization = request.headers['Authorization']
  if not authorization or not authorization.startswith('Bearer '):
    return make_response(False, 401, 'Thông tin xác thực không hợp lệ')
  
  token = authorization.split(' ')[1] if len(authorization.split(' ')) > 1 else ''
  decoded_token = decode_token(token)
  if not decode_token or decoded_token['exp'] < datetime.now().timestamp():
    return make_response(False, 401, 'Token đã hết hạn')
  
  user_id = decoded_token['user_id']
  try:
    user = User.objects.get(id=user_id)
  except:
    return make_response(False, 404, 'Người dùng không tồn tại')
  
  if user.role != 'candidate':
    return make_response(False, 403, 'Bạn không có quyền tạo mới hồ sơ ứng cử viên')

  name = request.data.get('name', None)
  phone = request.data.get('phone', None)
  description = request.data.get('description', None)
  address = request.data.get('address', None)
  position = request.data.get('position', None)
  gender = request.data.get('gender', None)
  email = request.data.get('email', None)
  birth_day = request.data.get('birthDay', None)
  
  files = request.FILES
  if files is None or 'avatar' not in files:
    return make_response(False, 400, 'Chưa có thông tin ảnh đại diện')
  avatar = files['avatar'] 
    
  candidate_profile_serializer = CandidateProfileSerializer(data={
    'user': user.id,
    'name': name,
    'phone': phone,
    'description': description,
    'address': address,
    'position': position,
    'gender': gender,
    'email': email,
    'birth_day': birth_day,
  })
  if candidate_profile_serializer.is_valid():
    try:
      candidate_profile = candidate_profile_serializer.save()
    except Exception as e:
      print('Error saving candidate profile:', e)
      return SERVER_ERROR_RESPONSE
    
    # Sau khi lưu thông tin hồ sơ ứng cử viên thành công, tiến hành lưu avatar lên firebase
    bucket = storage.bucket()
    avatar_filename = str(datetime.now().timestamp()) + os.path.basename(avatar.name)
    blob = bucket.blob('images/candidate_profile/' + avatar_filename)
    blob.upload_from_file(avatar, content_type=avatar.content_type)
    blob.make_public()

    candidate_profile.avatar = blob.public_url
    candidate_profile.save()

    return make_response(True, 201, 'Tạo hồ sơ ứng cử viên thành công!', CandidateProfileSerializer(candidate_profile).data)
  else:
    print(candidate_profile_serializer._errors)
    return make_response(False, 400, 'Thông tin không hợp lệ, vui lòng kiểm tra lại')

@api_view(['GET', 'PUT'])
def get_or_update_candidate_profile(request, id) -> Response:
  authorization = request.headers.get('Authorization', '')
  if not authorization or not authorization.startswith('Bearer '):
    return make_response(False, 401, 'Thông tin xác thực không hợp lệ')
  
  token = authorization.split(' ')[1]
  decoded_token = decode_token(token)
  if not decode_token or decoded_token['exp'] < datetime.now().timestamp():
    return make_response(False, 401, 'Token đã hết hạn')

  try:
    candidate_profile = CandidateProfile.objects.get(id=id)
  except CandidateProfile.DoesNotExist:
    return make_response(False, 404, 'Hồ sơ ứng viên không tồn tại')

  if request.method == 'GET':
    return make_response(True, 200, '', CandidateProfileSerializer(candidate_profile).data)
    
  user_id = decoded_token['user_id']
  try:
    candidate_profile = CandidateProfile.objects.get(id=id)
    user = User.objects.get(id=user_id)

  except CandidateProfile.DoesNotExist:
    return make_response(False, 404, 'Hồ sơ người dùng không tồn tại')
  except User.DoesNotExist:
    return make_response(False, 404, 'Người dùng không tồn tại')
  
  if user.role != 'candidate':
    return make_response(False, 403, 'Bạn không có quyền cập nhật hồ sơ ứng cử viên')

  serializer = CandidateProfileSerializer(candidate_profile, data=request.data, partial=True)
  
  if serializer.is_valid():
    try:
      candidate_profile = serializer.save()
      return make_response(True, 200, 'Cập nhật thành công!', CandidateProfileSerializer(candidate_profile).data)
    except Exception as e:
      print('Error saving candidate profile:', e)
      return SERVER_ERROR_RESPONSE
  else:
    print(serializer._errors)
    return make_response(False, 400, 'Thông tin không hợp lệ, vui lòng kiểm tra lại')


@api_view(['PUT'])
def update_avatar(request, id) -> Response:
  [is_authenticated, decoded_token, messagge] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, messagge)
  
  try:
    profile = CandidateProfile.objects.get(id=id)
  except CandidateProfile.DoesNotExist:
    return make_response(False, 404, 'Hồ sơ người dùng không tồn tại')
  if str(decoded_token['user_id']) != str(profile.user.id):
    return make_response(False, 403, 'Bạn không có quyền truy cập hồ sơ này', {
      'user_id': decoded_token['user_id'],
      'profile_id': profile.user.id
    })

  files = request.FILES
  if files is None or 'avatar' not in files:
    return make_response(False, 400, 'Chưa có thông tin ảnh đại diện')
  avatar = files['avatar']

  bucket = storage.bucket()
  avatar_filename = str(datetime.now().timestamp()) + os.path.basename(avatar.name)
  blob = bucket.blob('images/candidate_profile/' + avatar_filename)
  blob.upload_from_file(avatar, content_type=avatar.content_type)
  blob.make_public()

  old_avatar = profile.avatar
  profile.avatar = blob.public_url
  profile.save()

  delete_file(old_avatar)

  return make_response(True, 200, 'Cập nhật avatar thành công!', profile.avatar)
