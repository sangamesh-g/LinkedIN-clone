from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Custom user with LinkedIn-like profile fields.

    JSON fields store flexible, user-defined structures:
    - skills: list[str]
    - experiences: list[object]
    - educations: list[object]
    - websites: list[str]
    - contact: object
    """

    headline = models.CharField(max_length=140, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    industry = models.CharField(max_length=120, blank=True)
    profile_photo = models.URLField(blank=True)
    cover_photo = models.URLField(blank=True)

    skills = models.JSONField(default=list, blank=True)
    experiences = models.JSONField(default=list, blank=True)
    educations = models.JSONField(default=list, blank=True)
    websites = models.JSONField(default=list, blank=True)
    contact = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.username

# Create your models here.
