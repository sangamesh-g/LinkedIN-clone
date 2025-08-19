from django.urls import include, path
from .views import PostListCreate, PostDetail



urlpatterns = [
    # Placeholder: aggregate routes from sub-apps if needed
    path('accounts/', include('accounts.urls')),
    path('posts/', include('posts.urls')),
    path('connections/', include('connections.urls')),
    path('messaging/', include('messaging.urls')),
    path('jobs/', include('jobs.urls')),
    path('news/', include('news.urls')),
    # API-specific endpoints not tied to templates (demonstration)
    path('v1/posts/', PostListCreate.as_view()),
    path('v1/posts/<int:pk>/', PostDetail.as_view()),
]


