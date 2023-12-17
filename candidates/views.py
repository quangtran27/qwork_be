import os
from datetime import datetime
from uu import Error
from zoneinfo import available_timezones

from firebase_admin import storage
from rest_framework.decorators import api_view
from rest_framework.response import Response

from candidates.models import CandidateProfile
from candidates.serializers import CandidateProfileSerializer
from recruiters.models import RecruiterProfile
from users.models import User
from utils.api_response import make_response
from utils.firebase import delete_file
from utils.pagination import CustomPageNumberPagination
from utils.sample_data import SERVER_ERROR_RESPONSE
from utils.token import check_auth, decode_token
from django.db.models import Q

@api_view(['GET'])
def get_all_profiles(request):
  [is_authenticated, decoded_token, messagge] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, messagge)
  
  try:
    user = User.objects.get(id=decoded_token['user_id'])
    if user.role != 'recruiter':
      raise Exception('Tài khoản không có quyền truy cập')
  except:
    return make_response(False, 403, 'Tài khoản không có quyền truy cập')

  profiles = CandidateProfile.objects.filter(available=True, user__is_active=True)
  keyword = request.query_params.get('keyword')

  if keyword is not None:
    try:
      profiles = profiles.filter(Q(description__icontains=keyword) | Q(name__icontains=keyword) | Q(position__icontains=keyword))
    except Exception as e:
      print(e)

  try:
    paginator = CustomPageNumberPagination()
    result_page = paginator.paginate_queryset(profiles, request)
    return paginator.get_paginated_response(data=CandidateProfileSerializer(result_page, many=True).data)
  except:
    return make_response(False, 200, '', [])
  


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
    message = 'Thông tin không hợp lệ, vui lòng kiểm tra lại'

    errors = serializer._errors
    if 'phone' in errors and any(detail.code == 'unique' for detail in errors['phone']):
      message = 'Số điện thoại đã được sử dụng'
    if 'email' in errors and any(detail.code == 'unique' for detail in errors['email']):
      message = 'Email đã được sử dụng'
        
    print(serializer._errors)
    return make_response(False, 400, message)


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

  