from rest_framework.response import Response

SERVER_ERROR_RESPONSE = Response({
  'success': False,
  'message': 'Máy chủ xảy ra lỗi, vui lòng thử lại',
}, status=500)