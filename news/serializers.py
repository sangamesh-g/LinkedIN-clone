from rest_framework import serializers
from .models import NewsItem


class NewsItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = NewsItem
		fields = ['id', 'title', 'summary', 'url', 'source', 'meta', 'published_at', 'created_at']
		read_only_fields = ['id', 'created_at']


