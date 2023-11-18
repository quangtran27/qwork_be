from pkg_resources import require
from rest_framework import serializers
from users.models import User
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


class RequestResetPasswordSerializer(serializers.Serializer):
  email = serializers.EmailField(required=True)

  class Meta:
    fields = ['email',]

class SetNewPasswordSerializer(serializers.Serializer):
  password = serializers.CharField(min_length=6, max_length=68, write_only=True)
  token = serializers.CharField(min_length=1, write_only=True)
  email = serializers.EmailField()

  class Meta:
    fields = ['password', 'token', 'email']

  def validate(self, attrs):
    try:
      password = attrs.get('password')
      token = attrs.get('token')
      email = attrs.get('email')

      user = User.objects.get(email=email)
      if not PasswordResetTokenGenerator().check_token(user, token):
        raise AuthenticationFailed('The reset link is invalid', 401)

      user.set_password(password)
      user.save()

      return (user)
    except Exception as e:
      raise AuthenticationFailed('The reset link is invalid', 401)
    return super().validate(attrs)
