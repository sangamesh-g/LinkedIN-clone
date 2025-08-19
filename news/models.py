from django.db import models
from django.utils import timezone


class NewsItem(models.Model):
	title = models.CharField(max_length=240)
	summary = models.TextField(blank=True)
	url = models.URLField(blank=True)
	source = models.CharField(max_length=120, blank=True)
	meta = models.JSONField(default=dict, blank=True)
	published_at = models.DateTimeField(default=timezone.now)
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		ordering = ['-published_at']
