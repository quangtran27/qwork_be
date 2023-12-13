from django.urls import path

from . import views

urlpatterns = [
  path('login', views.login, name='login'),
  path('logout', views.logout, name='logout'),
  path('refresh-token', views.refresh_token, name='refresh_token'),
  path('change-password', views.change_password),
  path('reset-password', views.ResetPasswordApiView.as_view(), name='reset_password'),
]