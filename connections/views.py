from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Connection, Follow
from .serializers import ConnectionSerializer, FollowSerializer


class ConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = ConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Connection.objects.filter(recipient=user) | Connection.objects.filter(sender=user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        conn = self.get_object()
        if conn.recipient != request.user:
            return Response({'detail': 'Not allowed'}, status=403)
        conn.status = 'accepted'
        conn.save()
        return Response(ConnectionSerializer(conn).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        conn = self.get_object()
        if conn.recipient != request.user:
            return Response({'detail': 'Not allowed'}, status=403)
        conn.status = 'rejected'
        conn.save()
        return Response(ConnectionSerializer(conn).data)


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(follower=user) | Follow.objects.filter(followed=user)

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)
