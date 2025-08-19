from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Job, JobApplication
from .serializers import JobSerializer, JobApplicationSerializer


class IsPosterOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'posted_by', None) == request.user


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsPosterOrReadOnly]

    def get_queryset(self):
        return Job.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        job = self.get_object()
        serializer = JobApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save(job=job, applicant=request.user)
        return Response(JobApplicationSerializer(application).data, status=status.HTTP_201_CREATED)


class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return JobApplication.objects.filter(applicant=user) | JobApplication.objects.filter(job__posted_by=user)
