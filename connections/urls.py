from rest_framework.routers import DefaultRouter
from .views import ConnectionViewSet, FollowViewSet


router = DefaultRouter()
router.register(r'connections', ConnectionViewSet, basename='connection')
router.register(r'follows', FollowViewSet, basename='follow')

urlpatterns = router.urls


