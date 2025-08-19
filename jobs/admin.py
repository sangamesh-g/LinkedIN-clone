from django.contrib import admin
from .models import Job, JobApplication

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'company', 'posted_by', 'created_at')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
	list_display = ('id', 'job', 'applicant', 'status', 'created_at')
