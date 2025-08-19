from django.contrib import admin
from .models import Post, Tag

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'visibility', 'created_at')
    list_filter = ('visibility', 'created_at')
    readonly_fields = ('reactions', 'comments', 'reposts', 'shares')

    def get_reaction_count(self, obj):
        return obj.get_reaction_count()
    get_reaction_count.short_description = 'Reactions'

    def get_comment_count(self, obj):
        return obj.get_comment_count()
    get_comment_count.short_description = 'Comments'

    def get_repost_count(self, obj):
        return obj.get_repost_count()
    get_repost_count.short_description = 'Reposts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
