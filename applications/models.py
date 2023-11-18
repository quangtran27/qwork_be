import uuid

from django.db import models

from jobs.models import Job
from users.models import User
from users.validators import PhoneValidator

APPLICATION_STATUS_CHOICES = (
  (1, 'Đã nộp'),
  (2, 'Nhà tuyển dụng đã xem hồ sơ'),
  (3, 'Đã gửi lời mời phỏng vấn'),
  (4, 'Không được chấp nhận'),
)

class Application(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  job = models.ForeignKey(to=Job, on_delete=models.SET_NULL, null=True)
  user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  name = models.CharField(max_length=255)
  email = models.EmailField(max_length=255)
  phone = models.CharField(max_length=20, validators=[PhoneValidator])
  cv = models.URLField(max_length=1000, null=True, blank=True, default=None)
  status = models.IntegerField(choices=APPLICATION_STATUS_CHOICES, default=1)

  def __str__(self) -> str:
    return f'{self.user.name if self.user.name else ""} - {(self.job.name if self.job else "")}'
