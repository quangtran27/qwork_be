from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPageNumberPagination(PageNumberPagination):
  # page_query_param = 'page'
  
  def get_paginated_response(self, data):
    return Response({
      'data': data,
      'pagination': {
        'total': self.page.paginator.count,
        'page': int(self.request.query_params.get('page', '1')),
        'num_pages': self.page.paginator.num_pages,
      }
    })