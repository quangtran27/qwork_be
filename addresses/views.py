from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from django.http import JsonResponse

from utils.api_response import make_response

@api_view(['GET'])
def get_all_cities(request):
  
  # Data reference: https://danhmuchanhchinh.gso.gov.vn/
  external_api_url = 'https://provinces.open-api.vn/api/'

  try:
    response = requests.get(external_api_url)
    data = response.json()

    return make_response(True, 200, data=data)

  except:
    return Response({'error': 'Error happened'})