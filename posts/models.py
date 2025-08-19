from django.db import models
from django.conf import settings

# Create your models here.

class Tag(models.Model):
	name = models.CharField(max_length=64, unique=True)
	def __str__(self): return self.name

class Post(models.Model):
	VISIBILITY_CHOICES = [('public','Public'),('connections','Connections'),('private','Private')]
	REACTION_CHOICES = [('like','Like'),('celebrate','Celebrate'),('support','Support'),('love','Love'),('insightful','Insightful'),('curious','Curious')]
	
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
	text = models.TextField(blank=True)
	media = models.JSONField(default=list, blank=True)  # [{url, type}]
	visibility = models.CharField(max_length=16, choices=VISIBILITY_CHOICES, default='public')
	tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
	mentions = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='mentioned_in', blank=True)
	repost_of = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='repost_instances')
	
	# JSON fields for storing interactions
	reactions = models.JSONField(default=list, blank=True)  # [{"user_id": 1, "kind": "like", "created_at": "2024-01-01T00:00:00Z"}]
	comments = models.JSONField(default=list, blank=True)   # [{"id": 1, "user_id": 1, "text": "Great post!", "created_at": "2024-01-01T00:00:00Z", "replies": [{"user_id": 2, "text": "I agree!", "created_at": "2024-01-01T00:00:00Z"}]}]
	reposts = models.JSONField(default=list, blank=True)    # [{"user_id": 1, "created_at": "2024-01-01T00:00:00Z"}]
	shares = models.JSONField(default=list, blank=True)     # [{"user_id": 1, "to_user_id": 2, "created_at": "2024-01-01T00:00:00Z"}]
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		indexes = [models.Index(fields=['-created_at'])]

	def __str__(self):
		return f'{self.author} - {self.text[:30]}'
	
	def get_reaction_count(self, kind=None):
		"""Get count of reactions, optionally filtered by kind"""
		if kind:
			return len([r for r in self.reactions if r.get('kind') == kind])
		return len(self.reactions)
	
	def get_comment_count(self):
		"""Get total count of comments including replies"""
		total = len(self.comments)
		for comment in self.comments:
			total += len(comment.get('replies', []))
		return total
	
	def get_repost_count(self):
		"""Get count of reposts"""
		return len(self.reposts)
	
	def get_share_count(self):
		"""Get count of shares"""
		return len(self.shares)
	
	def has_user_reacted(self, user_id, kind=None):
		"""Check if user has reacted to this post"""
		for reaction in self.reactions:
			if reaction.get('user_id') == user_id:
				if kind is None or reaction.get('kind') == kind:
					return True
		return False
	
	def get_user_reaction(self, user_id):
		"""Get user's reaction kind if any"""
		for reaction in self.reactions:
			if reaction.get('user_id') == user_id:
				return reaction.get('kind')
		return None
