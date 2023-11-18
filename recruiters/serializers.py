from dataclasses import fields
from rest_framework import serializers

from recruiters.models import RecruiterProfile

class RecruiterProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = RecruiterProfile
    fields = (
      'id',
      'user_id',
      'avatar',
      'background',
      'name',
      'description',
      'phone',
      'email',
      'address',
    )