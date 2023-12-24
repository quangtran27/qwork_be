import os
from datetime import datetime

from firebase_admin import storage
from requests import Request
from rest_framework.decorators import api_view
from rest_framework.response import Response

from applications.models import Application
from applications.serialziers import ApplicationSerializer
from jobs.models import Job
from utils.api_response import make_response
from utils.sample_data import SERVER_ERROR_RESPONSE
from utils.token import check_auth, check_permissions


@api_view(['POST'])
def create_application(request) -> Response:
  [is_authenticated, decoded_token, messagge] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, messagge)
  
  if not check_permissions(decoded_token['user_id'], ['candidate']):
    return make_response(False, 403, 'Bạn không có quyền tạo mới đơn ứng tuyển')
  
  data = request.data
  data['user'] = decoded_token['user_id']

  try:
    job = Job.objects.get(id=request.data.get('job_id', None))
  except Job.DoesNotExist:
    return make_response(True, 400, 'Thông tin tuyển dụng không tồn tại')
  
  if datetime(job.expired.year, job.expired.month, job.expired.day) <= datetime.now():
    return make_response(False, 400, 'Tin tuyển dụng đã hết hạn!')
  
  old_cv = request.data.get('old_cv')
  if old_cv is None:
    files = request.FILES
    if files is None or 'cv' not in files:
      return make_response(False, 400, 'Chưa có thông tin CV')
    cv = files['cv']
    if cv.name.split('.')[1] not in ['doc', 'docx', 'pdf']:
      return make_response(False, 400, 'CV chưa đúng định dạng, chỉ châp nhận .doc, .docx và pdf')

  data['cv'] = None
  serializer = ApplicationSerializer(data=data)
  if serializer.is_valid():
    try:
      application: Application = serializer.save()
    except Exception as e:
      return SERVER_ERROR_RESPONSE
  else:
    return make_response(False, 400, 'Thông tin không hợp lệ, vui lòng kiểm tra lại')
  
  if old_cv is not None:
    application.cv = old_cv
  else:
    bucket = storage.bucket()
    timestamp = str(datetime.now().timestamp())
    blob = bucket.blob(f'cv/{timestamp}/{os.path.basename(cv.name)}')
    blob.upload_from_file(cv, content_type=cv.content_type)
    blob.make_public()
    application.cv = blob.public_url

  application.job = job
  application.save()
  return make_response(True, 201, 'Ứng tuyển thành công!', ApplicationSerializer(application).data)
  
@api_view(['GET', 'PUT', 'DELETE'])
def get_or_update_or_delete_application(request, id):
  [is_authenticated, decoded_token, message] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, message)
  
  try:
    application = Application.objects.get(id=id)
  except Application.DoesNotExist:
    return make_response(False, 404, 'Đơn ứng tuyển không tồn tại!')
  
  if request.method == 'GET':
    return make_response(True, 200, '', ApplicationSerializer(application).data)
  if request.method == 'DELETE':
    try:
      application.delete()
      return make_response(True, 200, 'Xoá thành công!')
    except:
      return SERVER_ERROR_RESPONSE

  if not check_permissions(decoded_token['user_id'], ['candidate', 'recruiter']):
    return make_response(False, 403, 'Bạn không có quyền truy cập đơn ứng tuyển này!')
  serializer = ApplicationSerializer(application, data=request.data, partial=True)
  if serializer.is_valid():
    try:
      application = serializer.save()
      return make_response(True, 200, 'Cập nhật thành công!', ApplicationSerializer(application).data)
    except:
      return SERVER_ERROR_RESPONSE
  else:
    return make_response(False, 400, 'Thông tin không hợp lệ, vui lòng kiểm tra lại!')
