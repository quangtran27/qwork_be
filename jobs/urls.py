from django.urls import path

from jobs.views import (JobList, get_job_applications,
                        get_or_update_or_delete_job, get_outstanding_jobs)

urlpatterns = [
  path('', JobList.as_view(), name='job_list'),
  path('outstanding', get_outstanding_jobs),
  path('<str:id>', get_or_update_or_delete_job),
  path('<str:id>/applications', get_job_applications),
]
