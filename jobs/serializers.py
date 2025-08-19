from rest_framework import serializers
from .models import Job, JobApplication


class JobSerializer(serializers.ModelSerializer):
	posted_by_name = serializers.CharField(source='posted_by.username', read_only=True)

	class Meta:
		model = Job
		fields = [
			'id', 'title', 'company', 'location', 'description', 'requirements', 'salary_range', 'is_remote',
			'posted_by', 'posted_by_name', 'created_at'
		]
		read_only_fields = ['id', 'posted_by', 'posted_by_name', 'created_at']


class JobApplicationSerializer(serializers.ModelSerializer):
	applicant_name = serializers.CharField(source='applicant.username', read_only=True)

	class Meta:
		model = JobApplication
		fields = ['id', 'job', 'applicant', 'applicant_name', 'resume_url', 'cover_letter', 'answers', 'status', 'created_at']
		read_only_fields = ['id', 'job', 'applicant', 'applicant_name', 'created_at']


