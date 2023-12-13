import uuid

from django.db import models

from users.models import User
from users.validators import PhoneValidator


class RecruiterProfile(models.Model):
  phone_validator = PhoneValidator()
  
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  user = models.OneToOneField(to=User, on_delete=models.PROTECT)
  avatar = models.URLField(blank=True, null=True)
  background = models.URLField(blank=True, null=True, default=None)
  name = models.CharField(max_length=255)
  description = models.TextField(blank=True)
  phone = models.CharField(max_length=20, unique=True, validators=[phone_validator])
  email = models.EmailField(max_length=255, unique=True)
  address = models.CharField(max_length=255)

  class Meta:
    ordering = ['name']

  def __str__(self) -> str:
    return self.name