from django.urls import path

from users.views import (active_user, get_or_update_user_saved_jobs,
                         get_user_application_cvs, get_user_applications,
                         get_user_profile, register, send_email_active,
                         update_user_info)

urlpatterns = [
  path('', register),
  path('<str:id>/info', update_user_info),
  path('active/<str:email>/<str:token>', active_user),
  path('<str:id>/profile', get_user_profile),
  path('<str:id>/applications', get_user_applications),
  path('<str:id>/saved-jobs', get_or_update_user_saved_jobs),
  path('<str:id>/cvs', get_user_application_cvs),
  path('<str:email>/send-active-email', send_email_active),
]