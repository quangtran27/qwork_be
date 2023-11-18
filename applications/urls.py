from django.urls import path

from applications.views import create_application, get_or_update_or_delete_application

urlpatterns = [
  path('', create_application),
  path('<str:id>', get_or_update_or_delete_application),
]
