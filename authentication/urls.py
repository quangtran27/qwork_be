from django.urls import path

from . import views

urlpatterns = [
  path('login', views.login, name='login'),
  path('logout', views.logout, name='logout'),
  path('refresh-token', views.refresh_token, name='refresh_token'),
  path('change-password', views.change_password),
  path('request-password-reset', views.request_reset_password),
  path('password-reset/<token>/<email>', views.check_reset_password_token, name='password-reset-confirm' ),
  path('password-reset-done', views.set_new_password, name='password_reset_done'),
]