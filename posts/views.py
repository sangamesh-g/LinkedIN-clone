from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Post, Tag
from .serializers import PostSerializer, TagSerializer, ReactionSerializer, CommentSerializer, ReplySerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.utils import timezone
import json

class PostViewSet(viewsets.ModelViewSet):
	queryset = Post.objects.all()
	serializer_class = PostSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)

	@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
	def comment(self, request, pk=None):
		post = self.get_object()
		serializer = CommentSerializer(data=request.data)
		if serializer.is_valid():
			comment_data = {
				'id': len(post.comments) + 1,  # Simple ID generation
				'user_id': request.user.id,
				'text': serializer.validated_data['text'],
				'created_at': timezone.now().isoformat(),
				'replies': []
			}
			post.comments.append(comment_data)
			post.save()
			return Response(comment_data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
	def reply(self, request, pk=None):
		post = self.get_object()
		comment_id = request.data.get('comment_id')
		text = request.data.get('text')
		
		if not comment_id or not text:
			return Response({'error': 'comment_id and text are required'}, status=status.HTTP_400_BAD_REQUEST)
		
		# Find the comment and add reply
		for comment in post.comments:
			if comment.get('id') == comment_id:
				reply_data = {
					'user_id': request.user.id,
					'text': text,
					'created_at': timezone.now().isoformat()
				}
				comment['replies'].append(reply_data)
				post.save()
				return Response(reply_data, status=status.HTTP_201_CREATED)
		
		return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

	@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
	def react(self, request, pk=None):
		post = self.get_object()
		kind = request.data.get('kind', 'like')
		
		# Remove existing reaction from this user
		post.reactions = [r for r in post.reactions if r.get('user_id') != request.user.id]
		
		# Add new reaction
		reaction_data = {
			'user_id': request.user.id,
			'kind': kind,
			'created_at': timezone.now().isoformat()
		}
		post.reactions.append(reaction_data)
		post.save()
		
		return Response(reaction_data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
	def repost(self, request, pk=None):
		original_post = self.get_object()
		
		# Check if user already reposted
		for repost in original_post.reposts:
			if repost.get('user_id') == request.user.id:
				return Response({'error': 'Already reposted'}, status=status.HTTP_400_BAD_REQUEST)
		
		# Add repost record
		repost_data = {
			'user_id': request.user.id,
			'created_at': timezone.now().isoformat()
		}
		original_post.reposts.append(repost_data)
		original_post.save()
		
		# Create new post as repost
		repost_post = Post.objects.create(
			author=request.user,
			text=original_post.text,
			media=original_post.media,
			visibility=original_post.visibility,
			repost_of=original_post
		)
		
		return Response(PostSerializer(repost_post).data, status=status.HTTP_201_CREATED)

	@action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
	def share(self, request, pk=None):
		post = self.get_object()
		to_user_id = request.data.get('to_user_id')
		
		if not to_user_id:
			return Response({'error': 'to_user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
		
		share_data = {
			'user_id': request.user.id,
			'to_user_id': to_user_id,
			'created_at': timezone.now().isoformat()
		}
		post.shares.append(share_data)
		post.save()
		
		return Response(share_data, status=status.HTTP_200_OK)

class TagViewSet(viewsets.ModelViewSet):
	queryset = Tag.objects.all()
	serializer_class = TagSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]

