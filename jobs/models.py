import uuid

from django.db import models

from users.models import User


class Job(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  user = models.ForeignKey(to=User, on_delete=models.PROTECT)
  name = models.CharField(max_length=255)
  description = models.TextField()
  city_code = models.PositiveSmallIntegerField()
  city_name = models.CharField(max_length=255, default='')
  salary_from = models.PositiveIntegerField() # đơn vị: Triệu
  salary_to = models.PositiveIntegerField() # đơn vị: Triệu
  created = models.DateField(auto_now_add=True)
  updated = models.DateField(auto_now=True)
  expired = models.DateField()
  status = models.BooleanField(default=True)

  class Meta:
    ordering = ['-created']

  def __str__(self) -> str:
    return self.name
