from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = (
      'id',
      'name',
      'phone',
      'email',
      'password',
      'role',
      'is_active',
    )

class UserInfoSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = (
      'name',
      'phone',
    )