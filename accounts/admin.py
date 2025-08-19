from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': (
                'headline', 'bio', 'location', 'industry',
                'profile_photo', 'cover_photo',
                'skills', 'experiences', 'educations', 'websites', 'contact',
                'created_at',
            )
        }),
    )
    readonly_fields = ('created_at',)

