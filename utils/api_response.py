from typing import Any, Optional, Union

from rest_framework.response import Response


def make_response(success: bool, code: int, message: str | None = None, data: Optional[Union[Any, None]] = None) -> Response:
  return Response({
    'success': success,
    'message': message,
    'data': data
  }, status=code)