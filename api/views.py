from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from posts.models import Post
from posts.serializers import PostSerializer


class PostListCreate(APIView):
    def get(self, request):
        queryset = Post.objects.all().order_by('-created_at')
        data = PostSerializer(queryset, many=True).data
        return Response(data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            # For API app independence, allow author id in payload; default to anonymous-like None
            author = request.user if request.user.is_authenticated else None
            serializer.save(author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return None

    def get(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response({'detail': 'Not found'}, status=404)
        return Response(PostSerializer(post).data)

    def put(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response({'detail': 'Not found'}, status=404)
        serializer = PostSerializer(post, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        post = self.get_object(pk)
        if not post:
            return Response({'detail': 'Not found'}, status=404)
        post.delete()
        return Response(status=204)
