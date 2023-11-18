from django.urls import path

from users.views import get_user_applications, get_user_profile, register

urlpatterns = [
  path('', register),
  path('<str:id>/profile', get_user_profile),
  path('<str:id>/applications', get_user_applications)
]