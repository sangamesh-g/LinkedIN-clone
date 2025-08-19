from django.db import models
from django.conf import settings
from django.utils import timezone


class Job(models.Model):
	title = models.CharField(max_length=160)
	company = models.CharField(max_length=160)
	location = models.CharField(max_length=160, blank=True)
	description = models.TextField()
	requirements = models.JSONField(default=list, blank=True)  # list of strings
	salary_range = models.CharField(max_length=120, blank=True)
	is_remote = models.BooleanField(default=False)
	posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs_posted')
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self) -> str:
		return f'{self.title} @ {self.company}'


class JobApplication(models.Model):
	job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
	applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')
	resume_url = models.URLField(blank=True)
	cover_letter = models.TextField(blank=True)
	answers = models.JSONField(default=dict, blank=True)
	status = models.CharField(max_length=32, default='submitted')
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		unique_together = ('job', 'applicant')
