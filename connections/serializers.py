from rest_framework import serializers
from .models import Connection, Follow


class ConnectionSerializer(serializers.ModelSerializer):
	sender_name = serializers.CharField(source='sender.username', read_only=True)
	recipient_name = serializers.CharField(source='recipient.username', read_only=True)

	class Meta:
		model = Connection
		fields = ['id', 'sender', 'sender_name', 'recipient', 'recipient_name', 'status', 'message', 'created_at']
		read_only_fields = ['id', 'sender', 'created_at', 'status']


class FollowSerializer(serializers.ModelSerializer):
	follower_name = serializers.CharField(source='follower.username', read_only=True)
	followed_name = serializers.CharField(source='followed.username', read_only=True)

	class Meta:
		model = Follow
		fields = ['id', 'follower', 'follower_name', 'followed', 'followed_name', 'created_at']
		read_only_fields = ['id', 'follower', 'created_at']


