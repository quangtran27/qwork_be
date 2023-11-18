from datetime import datetime
from typing import Any, Dict

import jwt
from requests import Request

from qwork_be.settings import SECRET_KEY
from users.models import User


def decode_token(token) -> Dict[str, Any] | None:
  try:
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return decoded_token
  except jwt.ExpiredSignatureError:
    print('Token has expired!')
  except jwt.DecodeError:
    print('Token cannot be decoded')
  return None

def check_auth(request):
  authorization = request.headers.get('Authorization', '')
  if not authorization or not authorization.startswith('Bearer'):
    return [False, None, 'Thông tin xác thực không hợp lệ']
  token = authorization.split(' ')[1]
  decoded_token = decode_token(token)
  if not decode_token or decoded_token['exp'] < datetime.now().timestamp():
    return [False, None, 'Token đã hết hạn']
  return [True, decoded_token, '']

def check_permissions(user_id, permissions: list[str]):
  try:
    user = User.objects.get(id=user_id)
  except User.DoesNotExist:
    pass
  if user.role in permissions:
    return True
  return False 
  