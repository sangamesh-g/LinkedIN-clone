from rest_framework.routers import DefaultRouter
from .views import JobViewSet, JobApplicationViewSet


router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'job-applications', JobApplicationViewSet, basename='job-application')

urlpatterns = router.urls


