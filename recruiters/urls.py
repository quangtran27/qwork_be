from django.urls import path

from recruiters.views import (RecruiterList, get_all_recruiter_profiles,
                              get_or_update_recruiter_profile,
                              get_outstanding_recruiters, get_recruiters_jobs,
                              update_avatar, update_background)

urlpatterns = [
  path('', RecruiterList.as_view()),
  path('outstanding', get_outstanding_recruiters),
  path('<str:id>', get_or_update_recruiter_profile),
  path('<str:id>/avatar', update_avatar),
  path('<str:id>/background',update_background),
  path('<str:id>/jobs', get_recruiters_jobs)
]