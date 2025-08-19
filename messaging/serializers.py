from rest_framework import serializers
from .models import Conversation, Message


class ConversationSerializer(serializers.ModelSerializer):
	participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

	class Meta:
		model = Conversation
		fields = ['id', 'participants', 'created_at']
		read_only_fields = ['id', 'created_at', 'participants']


class MessageSerializer(serializers.ModelSerializer):
	sender_name = serializers.CharField(source='sender.username', read_only=True)

	class Meta:
		model = Message
		fields = ['id', 'conversation', 'sender', 'sender_name', 'body', 'created_at', 'edited_at']
		read_only_fields = ['id', 'sender', 'created_at', 'edited_at', 'conversation']


