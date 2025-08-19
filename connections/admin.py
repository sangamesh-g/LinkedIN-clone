from django.contrib import admin
from .models import Connection, Follow

@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'followed', 'created_at')
