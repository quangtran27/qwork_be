import os
from base64 import urlsafe_b64decode
from crypt import methods
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponsePermanentRedirect
from django.urls import reverse
from django.utils.encoding import (DjangoUnicodeDecodeError, smart_bytes,
                                   smart_str)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_yasg.utils import swagger_auto_schema
from requests import Request
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.serializers import (RequestResetPasswordSerializer,
                                        SetNewPasswordSerializer)
from authentication.utils import Util
from users.models import User
from utils.api_response import make_response
from utils.sample_data import SERVER_ERROR_RESPONSE
from utils.token import check_auth


class CustomRedirect(HttpResponsePermanentRedirect):
  allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']

def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
    'access': str(refresh.access_token),
    'refresh': str(refresh),
  }

@api_view(['POST'])
def login(request):
  data = request.data
  email = data.get('email', None)
  password = data.get('password', None)
  role = data.get('role', None)

  user = authenticate(username=email, password=password)
  print(user)
  if user is not None and user.role == role:
    if user.is_active:
      token_data = get_tokens_for_user(user)

      response = make_response(True, 200, 'Đăng nhập thành công!', {
        'id': user.id,
        'name': user.name,
        'role': user.role,
        'token': token_data['access']
      })

      response.set_cookie(
        key = settings.SIMPLE_JWT['AUTH_COOKIE'],
        value = token_data['refresh'],
        expires = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
      )

      return response
    else:
      return make_response(False, 404, 'Tài khoản của bạn đã bị vô hiệu hóa!')
  else:
    return make_response(False, 404, 'Email hoặc mật khẩu chưa chính xác!')

@api_view(['POST'])
def refresh_token(request):
  refresh_token_value = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
  if refresh_token_value:
    try:
      old_refresh_token = RefreshToken(refresh_token_value)
      user_id = old_refresh_token['user_id']
      # old_refresh_token.blacklist()

      try:
        user = User.objects.get(id=user_id)
        new_token_data = get_tokens_for_user(user)

        response = make_response(True, 200, 'Đăng nhập thành công!', {
          'id': user.id,
          'name': user.name,
          'role': user.role,
          'token': new_token_data['access']
        })

        response.set_cookie(
          key = settings.SIMPLE_JWT['AUTH_COOKIE'],
          value = new_token_data['refresh'],
          expires = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
          secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
          httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
          samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )

        return response
      except User.DoesNotExist:
        return make_response(False, 404, 'Không tìm thấy người dùng!')
    except Exception as e:
      print(e)
      return make_response(False, 400, 'Refresh token không hợp lệ!')
  else:
    return make_response(False, 400, 'Không tìm thấy refresh token!')

@api_view(['POST'])
def logout(request):
  response = Response(status=status.HTTP_200_OK)
  response.set_cookie(
    key = settings.SIMPLE_JWT['AUTH_COOKIE'],
    value = '',
    expires = timedelta(seconds=1),
    secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
    httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
    samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
  )
  return response

@api_view(['PUT'])
def change_password(request: Request) -> Response:
  [is_authenticated, decoded_token, messagge] = check_auth(request)
  if not is_authenticated:
    return make_response(False, 401, messagge)
  
  try:
    user = User.objects.get(id=decoded_token['user_id'])
  except:
    return make_response(False, 404, 'Người dùng không tồn tại')

  if user.role not in ['recruiter', 'candidate']:
    return make_response(False, 403, 'Bạn không có quyền cập nhật hồ sơ nhà tuyển dụng')

  data = request.data
  print('old_password' not in data)
  
  if ('old_password' not in data) or ('new_password' not in data) or (data['old_password'] == data['new_password']):
    return make_response(False, 400, 'Dữ liệu không hợp lệ')
  if not user.check_password(data['old_password']):
    return make_response(False, 400, 'Mật khẩu cũ không chính xác')
  
  user.password = make_password(data['new_password'])
  user.save()

  return make_response(True, 200, 'Cập nhật mật khẩu thành công')

@swagger_auto_schema(method='POST', request_body=RequestResetPasswordSerializer)
@api_view(['POST'])
def request_reset_password(request):
  serializer = RequestResetPasswordSerializer(data=request.data)
  if not serializer.is_valid():
    return make_response(False, 400, 'Vui lòng nhập email')
  
  email = request.data.get('email')

  if not User.objects.filter(email=email).exists():
    return make_response(False, 404, 'Tài khoản với email này không tồn tại!')
  
  user = User.objects.get(email=email)
  token = PasswordResetTokenGenerator().make_token(user)
  email_body = f'Xin chào {user.name},\nHãy sử dụng Bạn hãy sử mã này để đặt mật khẩu của mình: {token}'
  data = {
    'email_body': email_body,
    'to_email': user.email,
    'email_subject': 'Đặt lại mật khẩu'
  }
  Util.send_email(data)
  return make_response(True, 201, 'Chúng tôi đã gửi cho bạn đường dẫn đặt lại mật khẩu trong email', user.email)

@api_view(['GET'])
def check_reset_password_token(request, email, token):
  try:
    user = User.objects.get(email=email)
  except User.DoesNotExist():
    return make_response(False, '404', 'Tài khoản với email này không tồn tại!')

  try:
    if not PasswordResetTokenGenerator().check_token(user, token):
      return make_response(False, 400, 'Token không hợp lệ, vui lòng tạo một yêu cầu mới')
    return make_response(True, 200, 'Thông tin hợp lệ')
  except:
    return SERVER_ERROR_RESPONSE

@swagger_auto_schema(method='PATCH', request_body=SetNewPasswordSerializer)
@api_view(['PATCH'])
def set_new_password(request):
  serializer = SetNewPasswordSerializer(data=request.data)
  if serializer.is_valid():
    return make_response(True, 200, 'Cập nhật mật khẩu thành công')
  else:
    return make_response(False, 401, 'Mã xác đã được sử dụng')