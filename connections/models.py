from django.db import models
from django.conf import settings
from django.utils import timezone


class Connection(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('accepted', 'Accepted'),
		('rejected', 'Rejected'),
	]
	sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_connections')
	recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_connections')
	status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending')
	message = models.CharField(max_length=280, blank=True)
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		unique_together = ('sender', 'recipient')

	def __str__(self) -> str:
		return f'{self.sender} -> {self.recipient} ({self.status})'


class Follow(models.Model):
	follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
	followed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		unique_together = ('follower', 'followed')
