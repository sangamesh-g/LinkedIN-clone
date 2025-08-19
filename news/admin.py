from django.contrib import admin
from .models import NewsItem


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'source', 'published_at')
