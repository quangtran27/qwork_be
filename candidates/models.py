import uuid

from django.db import models

from jobs.models import Job
from users.models import User
from users.validators import PhoneValidator

GENDER_CHOICES = (('male', 'Nam'), ('famele', 'Nữ'))

class CandidateProfile(models.Model):
  phone_validator = PhoneValidator()

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  user = models.OneToOneField(to=User, on_delete=models.CASCADE)
  avatar = models.URLField(null=True, blank=True, default=None)
  name = models.CharField(max_length=255)
  description = models.TextField(blank=True)
  phone = models.CharField(max_length=20, unique=True, validators=[phone_validator])
  address = models.CharField(max_length=255)
  position = models.CharField(max_length=255)
  gender = models.CharField(choices=GENDER_CHOICES, default='male')
  birth_day = models.DateField(null=True, blank=True)
  email = models.EmailField(max_length=255, unique=True)
  available = models.BooleanField(default=False)

  saved_jobs = models.ManyToManyField(Job, blank=True)

  class Meta:
    ordering = ['name']

  def __str__(self) -> str:
    return self.user.name

class Test(models.Model):
  name = models.CharField(max_length=255)
  image = models.URLField()