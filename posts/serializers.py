from rest_framework import serializers
from .models import Post, Tag
from accounts.models import User

class TagSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tag
		fields = ['id','name']

class PostSerializer(serializers.ModelSerializer):
	author_name = serializers.CharField(source='author.username', read_only=True)
	author_full_name = serializers.SerializerMethodField()
	reaction_count = serializers.SerializerMethodField()
	comment_count = serializers.SerializerMethodField()
	repost_count = serializers.SerializerMethodField()
	share_count = serializers.SerializerMethodField()
	user_reaction = serializers.SerializerMethodField()
	tags = TagSerializer(many=True, required=False)
	repost_of = serializers.PrimaryKeyRelatedField(read_only=True)

	class Meta:
		model = Post
		fields = ['id','author','author_name','author_full_name','text','media','visibility','tags','mentions','repost_of','created_at','updated_at','reaction_count','comment_count','repost_count','share_count','user_reaction','reactions','comments','reposts','shares']
		read_only_fields = ['id','author','created_at','updated_at','reaction_count','comment_count','repost_count','share_count','user_reaction','reactions','comments','reposts','shares']

	def get_author_full_name(self, obj):
		return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username

	def get_reaction_count(self, obj):
		return obj.get_reaction_count()

	def get_comment_count(self, obj):
		return obj.get_comment_count()

	def get_repost_count(self, obj):
		return obj.get_repost_count()

	def get_share_count(self, obj):
		return obj.get_share_count()

	def get_user_reaction(self, obj):
		request = self.context.get('request')
		if request and request.user.is_authenticated:
			return obj.get_user_reaction(request.user.id)
		return None

	def create(self, validated_data):
		tags_data = validated_data.pop('tags', [])
		post = Post.objects.create(**validated_data)
		for t in tags_data:
			tag, _ = Tag.objects.get_or_create(name=t['name'])
			post.tags.add(tag)
		return post

class ReactionSerializer(serializers.Serializer):
	kind = serializers.ChoiceField(choices=Post.REACTION_CHOICES)
	user_id = serializers.IntegerField(read_only=True)
	created_at = serializers.DateTimeField(read_only=True)

class CommentSerializer(serializers.Serializer):
	text = serializers.CharField(max_length=1000)
	user_id = serializers.IntegerField(read_only=True)
	created_at = serializers.DateTimeField(read_only=True)
	replies = serializers.ListField(read_only=True)

class ReplySerializer(serializers.Serializer):
	text = serializers.CharField(max_length=500)
	user_id = serializers.IntegerField(read_only=True)
	created_at = serializers.DateTimeField(read_only=True)