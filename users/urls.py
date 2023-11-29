from django.urls import path

from users.views import (get_or_update_user_saved_jobs, get_user_applications,
                         get_user_profile, register)

urlpatterns = [
  path('', register),
  path('<str:id>/profile', get_user_profile),
  path('<str:id>/applications', get_user_applications),
  path('<str:id>/saved-jobs', get_or_update_user_saved_jobs),
]