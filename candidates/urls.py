from django.urls import path

from .views import (get_all_profiles, get_or_update_candidate_profile,
                    update_avatar)

urlpatterns = [
  path('', get_all_profiles),
  path('<str:id>', get_or_update_candidate_profile),
  path('<str:id>/avatar', update_avatar)
]