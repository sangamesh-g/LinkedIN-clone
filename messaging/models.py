from django.db import models
from django.conf import settings
from django.utils import timezone


class Conversation(models.Model):
	participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self) -> str:
		return f'Conversation {self.id}'


class Message(models.Model):
	conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
	sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
	body = models.JSONField(default=dict)  # {"text": str, "attachments": [{url, type}], ...}
	created_at = models.DateTimeField(default=timezone.now)
	edited_at = models.DateTimeField(null=True, blank=True)
	is_read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='read_messages', blank=True)

	class Meta:
		ordering = ['created_at']
