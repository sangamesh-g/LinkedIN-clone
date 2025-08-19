"""
URL configuration for LinkedIn project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import signin_view, signup_view, logout_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    index_view, main_view, network_view, jobs_view, messaging_view,
    notifications_view, profile_view, user_profile_view, search_view,
    connect_send_view, connect_accept_view, connect_reject_view,
    post_react_view, post_comment_view, post_reply_view, post_repost_view, post_send_view,
    get_comments_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    
    # JWT Token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('', index_view),
    path('signin', signin_view),
    path('signup', signup_view),
    path('logout', logout_view),
    path('main', main_view),
    path('network', network_view),
    path('jobs', jobs_view),
    path('messaging', messaging_view),
    path('notifications', notifications_view),
    path('me', profile_view),
    path('u/<str:username>', user_profile_view),
    path('search', search_view),
    path('connect/send/<int:user_id>', connect_send_view),
    path('connect/accept/<int:pk>', connect_accept_view),
    path('connect/reject/<int:pk>', connect_reject_view),
    path('p/<int:post_id>/react', post_react_view),
    path('p/<int:post_id>/comment', post_comment_view),
    path('p/<int:post_id>/reply', post_reply_view),
    path('p/<int:post_id>/repost', post_repost_view),
    path('p/<int:post_id>/send', post_send_view),
    path('p/<int:post_id>/comments', get_comments_view),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
