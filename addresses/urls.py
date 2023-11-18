from django.urls import path

from .views import get_all_cities

urlpatterns = [
  path('cities', get_all_cities)
]
