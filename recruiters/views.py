import os
from datetime import datetime

from firebase_admin import storage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from applications.serialziers import ApplicationDetailSerializer
from jobs.serializers import JobDetailSerializer
from recruiters.models import RecruiterProfile
from recruiters.serializers import RecruiterProfileSerializer
from utils.api_response import make_response
from utils.firebase import delete_file
from utils.pagination import CustomPageNumberPagination
from utils.sample_data import SERVER_ERROR_RESPONSE
from utils.token import check_auth, check_permissions
from utils.validators import is_valid_uuid


def paginate_profiles(profiles, request):
  try:
    paginator = CustomPageNumberPagination()
    result_page = paginator.paginate_queryset(profiles, request)
    return paginator.get_paginated_response(data=RecruiterProfileSerializer(result_page, many=True).data)
  except Exception as e:
    print(e)
    return make_response(False, 200, '', [])
  
class RecruiterList(APIView):
  def get(self, request):
    profiles = RecruiterProfile.objects.all()
    keyword = request.query_params.get('keyword')

    if keyword is not None:
      try:
        profiles = profiles.filter(name__icontains=keyword)
      except Exception as e:
        print(e)

    return paginate_profiles(profiles, request)


@api_view(['GET'])
def get_all_recruiter_profiles(request):
  profiles = RecruiterProfile.objects.all()
  return paginate_profiles(profiles, request)

@api_view(['GET', 'PUT'])
def get_or_update_recruiter_profile(request, id) -> Response:
  [is_authenticated, decoded_token, messagge] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, messagge)

  try:
    profile = RecruiterProfile.objects.get(id=id)
  except RecruiterProfile.DoesNotExist:
    return make_response(False, 404, 'Hồ sơ nhà tuyển dụng không tồn tại!')
  
  if request.method == 'GET':
    return make_response(True, 200, '', RecruiterProfileSerializer(profile).data)

  if not check_permissions(decoded_token['user_id'], ['recruiter']) or str(decoded_token['user_id']) != str(profile.user.id):
    return make_response(False, 403, 'Bạn không có quyền truy cập hồ sơ nhà tuyển dụng này!')

  serializer = RecruiterProfileSerializer(profile, data=request.data, partial=True)
  if serializer.is_valid():
    try:
      profile = serializer.save()
      return make_response(True, 200, 'Cập nhật thành công!', RecruiterProfileSerializer(profile).data)
    except Exception as e:
      print('Error saving recruiter profile:', e)
      return SERVER_ERROR_RESPONSE
  else:
    print(serializer._errors)
    return make_response(False, 400, 'Thông tin không hợp lệ, vui lòng kiểm tra lại!')

@api_view(['PUT'])
def update_avatar(request, id) -> Response:
  [is_authenticated, decoded_token, messagge] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, messagge)
  try:
    profile = RecruiterProfile.objects.get(id=id)
  except RecruiterProfile.DoesNotExist:
    return make_response(False, 404, 'Hồ sơ nhà tuyển dụng không tồn tại!')

  if not check_permissions(decoded_token['user_id'], ['recruiter']) or str(decoded_token['user_id']) != str(profile.user.id):
    return make_response(False, 403, 'Bạn không có quyền truy cập hồ sơ nhà tuyển dụng này!')
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

@api_view(['PUT'])
def update_background(request, id) -> Response:
  [is_authenticated, decoded_token, messagge] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, messagge)
  try:
    profile = RecruiterProfile.objects.get(id=id)
  except RecruiterProfile.DoesNotExist:
    return make_response(False, 404, 'Hồ sơ nhà tuyển dụng không tồn tại!')

  if not check_permissions(decoded_token['user_id'], ['recruiter']) or str(decoded_token['user_id']) != str(profile.user.id):
    return make_response(False, 403, 'Bạn không có quyền truy cập hồ sơ nhà tuyển dụng này!')
  files = request.FILES
  if files is None or 'background' not in files:
    return make_response(False, 400, 'Chưa có thông tin ảnh đại diện')
  background = files['background']

  bucket = storage.bucket()
  background_filename = str(datetime.now().timestamp()) + os.path.basename(background.name)
  blob = bucket.blob('images/candidate_profile/' + background_filename)
  blob.upload_from_file(background, content_type=background.content_type)
  blob.make_public()

  old_background = profile.background
  profile.background = blob.public_url
  profile.save()
  delete_file(old_background)

  return make_response(True, 200, 'Cập nhật ảnh bìa thành công!', profile.background)
  
@api_view(['GET'])
def get_outstanding_recruiters(request) -> Response:
  recruiters = RecruiterProfile.objects.all()[:8]
  return make_response(True, 200, data=RecruiterProfileSerializer(recruiters, many=True).data)

@api_view(['GET'])
def get_recruiters_jobs(request, id) -> Response:
  if not is_valid_uuid(id):
    return make_response(False, 404, 'Nhà tuyển dụng không tồn tại')

  try:
    recruiter = RecruiterProfile.objects.get(id=id)
  except RecruiterProfile.DoesNotExist:
    return make_response(False, 404, 'Nhà tuyển dụng không tồn tại')

  jobs = recruiter.user.job_set.all()
  data = JobDetailSerializer(jobs, many=True).data
  for index, job in enumerate(jobs):
    data[index]['applications'] = ApplicationDetailSerializer(job.application_set.all(), many=True).data

  return make_response(True, 200, '', data)