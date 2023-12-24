from uuid import UUID

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime

from applications.serialziers import ApplicationDetailSerializer
from jobs import middleware
from jobs.models import Job
from jobs.serializers import JobDetailSerializer, JobSerializer
from utils.api_response import make_response
from utils.pagination import CustomPageNumberPagination
from utils.sample_data import SERVER_ERROR_RESPONSE
from utils.token import check_auth, check_permissions
from utils.validators import is_valid_uuid


def paginate_jobs(jobs, request):
  try:
    paginator = CustomPageNumberPagination()
    result_page = paginator.paginate_queryset(jobs, request)
    return paginator.get_paginated_response(data=JobDetailSerializer(result_page, many=True).data)
  except:
    return make_response(False, 200, '', [])

class JobList(APIView):
  def get(self, request):
    jobs = Job.objects.filter(status=True)
    keyword = request.query_params.get('keyword')
    city = request.query_params.get('city')

    if keyword is not None:
      try:
        jobs = jobs.filter(name__icontains=keyword)
      except Exception as e: 
        print(e)

    if city is not None and city != '0':
      try:
        jobs = jobs.filter(city_code=int(city, base=10))
      except Exception as e:
        print(e)

    return paginate_jobs(jobs, request)

  def post(self, request):
    [is_authenticated, decoded_token, messagge] = check_auth(request)
    if not is_authenticated:
      return make_response(False, 401, messagge)
    
    if not check_permissions(decoded_token['user_id'], ['recruiter']):
      return make_response(False, 403, 'Bạn không có quyền tạo mới tin tuyển dụng!')

    # expired = request.data['expired']
    # is_expired_valid = True
    # if expired is None: is_expired_valid = False
    # else:
    #   try:
    #     date_object = datetime.strptime(expired, '%Y-%m-%d')
    #     if date_object > datetime.now():
    #       is_expired_valid = False
    #   except:
    #     return make_response(False, 400, 'Thông tin ngày hết hạn không đúng định dạng')

    # if not is_expired_valid:
    #   return make_response(False, 400, 'Thông tin ngày hết hạn không hợp lệ')

    request.data['user']= decoded_token['user_id']
    serializer = JobSerializer(data=request.data)
    if serializer.is_valid():
      try:
        job = serializer.save()
        return make_response(True, 201, 'Tạo mới tin tuyển dụng thành công!', JobSerializer(job).data)
      except Exception as e:
        print('Error saving job:', e)
        return SERVER_ERROR_RESPONSE
    else:
      print(serializer._errors)
      return make_response(False, 400, 'Thông tin không hợp lệ')

@api_view(['GET', 'POST'])
def get_all_or_create_job(request) -> Response:
  if request.method == 'GET':
    jobs = Job.objects.all()
    
    try:
      paginator = CustomPageNumberPagination()
      result_page = paginator.paginate_queryset(jobs, request)
      return paginator.get_paginated_response(data=JobDetailSerializer(result_page, many=True).data)
    except Exception as e:
      print(e)
      return make_response(False, 200, 'Đã xảy ra lỗi khi tải danh sách công việc', [])
  
  [is_authenticated, decoded_token, messagge] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, messagge)
  
  if not check_permissions(decoded_token['user_id'], ['recruiter']):
    return make_response(False, 403, 'Bạn không có quyền tạo mới tin tuyển dụng!')

  request = middleware.middleware(request)
  
  request.data['user']= decoded_token['user_id']
  serializer = JobSerializer(data=request.data)
  if serializer.is_valid():
    try:
      job = serializer.save()
      return make_response(True, 201, 'Tạo mới tin tuyển dụng thành công!', JobSerializer(job).data)
    except Exception as e:
      print('Error saving job:', e)
      return SERVER_ERROR_RESPONSE
  else:
    print(serializer._errors)
    return make_response(False, 400, 'Thông tin không hợp lệ')

@api_view([ 'GET', 'PUT', 'DELETE' ])
def get_or_update_or_delete_job(request, id) -> Response:
  if not is_valid_uuid(id):
    return make_response(False, 404, 'Tin tuyển dụng không tồn tại')
  
  try:
    job = Job.objects.get(id=UUID(id))
  except Job.DoesNotExist:
    return make_response(False, 404, 'Tin tuyển dụng không tồn tại')    
  
  if request.method == 'GET':
    return make_response(True, 200, '', JobDetailSerializer(job).data)
  
  [is_authenticated, decoded_token, messagge] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, messagge)
  if not check_permissions(decoded_token['user_id'], ['recruiter']) or str(decoded_token['user_id']) != str(job.user.id):
    return make_response(False, 403, 'Bạn không có quyền truy cập tin tuyển dụng này!')

  if request.method == 'DELETE':
    try:
      job.delete()
      return make_response(True, 200, 'Xoá thành công!')
    except:
      return SERVER_ERROR_RESPONSE

  serializer = JobSerializer(job, data=request.data, partial=True)
  if serializer.is_valid():
    try:
      job = serializer.save()
      return make_response(True, 200, 'Cập nhật thành công!', JobSerializer(job).data)
    except Exception as e:
      print('Error saving job:', e)
  else:
    print(serializer._errors) 
    return make_response(False, 400, 'Thông tin không hợp lệ, vui lòng kiểm tra lại')

@api_view(['GET'])
def get_outstanding_jobs(request) -> Response:
  jobs = Job.objects.all().order_by('-created')[:9]
  return make_response(True, 200, '', data=JobDetailSerializer(jobs, many=True).data)

@api_view(['GET'])
def get_job_applications(request, id) -> Response:
  if not is_valid_uuid(id):
    return make_response(False, 404, 'Tin tuyển dụng không tồn tại')

  [is_authenticated, decoded_token, messagge] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, messagge)

  try:
    job = Job.objects.get(id=UUID(id))
  except Job.DoesNotExist:
    return make_response(False, 404, 'Tin tuyển dụng không tồn tại')

  if str(job.user.id) != str(decoded_token['user_id']):
    return make_response(False, 403, 'Bạn không có quyền truy cập vào tài nguyên này') 

  applications = job.application_set.all()
  
  return make_response(True, 200, '', ApplicationDetailSerializer(applications, many=True).data)
