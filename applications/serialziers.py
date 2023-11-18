from rest_framework import serializers

from applications.models import Application

class ApplicationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Application
    fields = '__all__'

class ApplicationDetailSerializer(serializers.ModelSerializer):
  job_name = serializers.CharField(source='job.name')
  job_salary_from = serializers.IntegerField(source='job.salary_from')
  job_salary_to = serializers.IntegerField(source='job.salary_to')
  recruiter_user_id = serializers.CharField(source='job.user.id')
  recruiter_avatar = serializers.CharField(source='job.user.recruiterprofile.avatar')
  recruiter_name = serializers.CharField(source='job.user.recruiterprofile.name')
  created = serializers.SerializerMethodField()
  updated = serializers.SerializerMethodField()
  candidate_avatar = serializers.URLField(source='user.candidateprofile.avatar')
  candidate_user_id = serializers.CharField(source='user.id')
  candidate_name = serializers.CharField(source='user.candidateprofile.name')
  
  def get_created(self, obj: Application):
    return obj.created.__format__('%d/%m/%Y %H:%M')
  def get_updated(self, obj: Application):
    return obj.updated.__format__('%d/%m/%Y %H:%M')

  class Meta:
    model = Application
    fields = (
      'id',
      'job_id',
      'job_name',
      'job_salary_from',
      'job_salary_to',
      'recruiter_user_id',
      'recruiter_avatar',
      'recruiter_name',
      'created',
      'updated',
      'email',
      'candidate_avatar',
      'candidate_user_id',
      'candidate_name',
      'name',
      'phone',
      'cv',
      'status',
    )

    