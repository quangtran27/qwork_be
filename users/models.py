import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import PhoneValidator

USER_ROLE_CHOICES = (
  ('admin', 'Quản trị viên'),
  ('staff', 'Nhân viên'),
  ('recruiter', 'Nhà tuyển dụng'),
  ('candidate', 'Ứng cử viên'),
)

class CustomUserManager(BaseUserManager):
  '''
    Custom user model manager where phone is the unique identifiers
    for authentication instead of usernames.
  '''
  def create_user(self, email, password, **extra_fields):
    '''
      Create and save a user with the given email and password.
    '''
    if not email:
      raise ValueError(_('The email must be set'))
    
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save()

    return user
  
  def create_superuser(self, email, password, **extra_fields):
    '''
      Create and save a SuperUser with the given email and password.
    '''
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)
    extra_fields.setdefault('is_active', True)

    if extra_fields.get('is_staff') is not True:
      raise ValueError(_('Superuser must have is_staff=True.'))
    if extra_fields.get('is_superuser') is not True:
      raise ValueError(_('Superuser must have is_superuser=True.'))

    return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
  phone_validator = PhoneValidator()

  username = None
  first_name = None
  last_name = None

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  email = models.EmailField(max_length=255, unique=True)
  phone = models.CharField(max_length=20, unique=True, validators=[PhoneValidator])
  name = models.CharField(max_length=255)
  role = models.CharField(choices=USER_ROLE_CHOICES, default='candidate')
  
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []

  objects = CustomUserManager()

  class Meta:
    ordering = ['email']

  def __str__(self) -> str:
    return self.email