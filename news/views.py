from rest_framework import viewsets, permissions
from .models import NewsItem
from .serializers import NewsItemSerializer


class NewsItemViewSet(viewsets.ModelViewSet):
    queryset = NewsItem.objects.all()
    serializer_class = NewsItemSerializer
    permission_classes = [permissions.IsAuthenticated]
