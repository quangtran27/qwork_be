from rest_framework import serializers

from candidates.models import CandidateProfile


class CandidateProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = CandidateProfile
    fields = (
      'id',
      'user_id',
      'avatar',
      'name',
      'phone',
      'description',
      'address',
      'position',
      'gender',
      'birth_day',
      'email',
      'available'
    )