from rest_framework import serializers

from jobs.models import Job


class JobSerializer(serializers.ModelSerializer):
  class Meta:
    model = Job
    fields = '__all__'

class JobDetailSerializer(serializers.ModelSerializer):
  recruiter_id = serializers.CharField(source='user.recruiterprofile.user_id')
  recruiter_name = serializers.CharField(source='user.recruiterprofile.name')
  recruiter_avatar = serializers.CharField(source='user.recruiterprofile.avatar')
  updated = serializers.SerializerMethodField()
  expired = serializers.SerializerMethodField()

  def get_updated(self, obj: Job):
    return obj.created.__format__('%d/%m/%Y') 
  def get_expired(self, obj: Job):
    return obj.expired.__format__('%d/%m/%Y') 
  
  class Meta:
    model = Job
    fields = (
      'id',
      'name',
      'user_id',
      'recruiter_id',
      'recruiter_name',
      'recruiter_avatar',
      'description',
      'city_code',
      'city_name',
      'salary_from',
      'salary_to',
      'updated',
      'created',
      'expired',
      'status',
    )