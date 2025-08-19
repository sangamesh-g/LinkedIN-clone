from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from django.contrib.auth import get_user_model
from pathlib import Path
from posts.models import Post, Tag
from news.models import NewsItem
from jobs.models import Job
from connections.models import Connection
from messaging.models import Conversation, Message
from django.http import JsonResponse
import json


def index_view(request):
    return render(request, 'index.html')


@login_required
def main_view(request):
    # Create a post (text + optional single media photo/video)
    if request.method == 'POST' and request.POST.get('action') == 'create_post':
        text = request.POST.get('text', '').strip()
        visibility = request.POST.get('visibility', 'public')
        tag_str = request.POST.get('tags', '')
        media_kind = request.POST.get('media_kind', 'none')  # 'photo' | 'video' | 'none'
        media_file = request.FILES.get('media_file')

        media_list = []
        if media_kind in ('photo', 'video') and media_file:
            user_dir = Path(settings.BASE_DIR) / 'static' / 'uploads' / request.user.username
            user_dir.mkdir(parents=True, exist_ok=True)
            file_name = f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{media_file.name}"
            file_path = user_dir / file_name
            with open(file_path, 'wb') as out:
                for chunk in media_file.chunks():
                    out.write(chunk)
            media_url = f"/static/uploads/{request.user.username}/{file_name}"
            media_list = [{"url": media_url, "type": media_kind}]

        post = Post.objects.create(author=request.user, text=text, visibility=visibility, media=media_list)

        # Tags
        for t in [s.strip() for s in tag_str.split(',') if s.strip()]:
            tag, _ = Tag.objects.get_or_create(name=t)
            post.tags.add(tag)
        return redirect('/main')

    # Feed: only connections' posts; if none, show empty note
    connected_user_ids = set()
    for c in Connection.objects.filter(status='accepted').filter(sender=request.user) | Connection.objects.filter(status='accepted').filter(recipient=request.user):
        if c.sender_id != request.user.id:
            connected_user_ids.add(c.sender_id)
        if c.recipient_id != request.user.id:
            connected_user_ids.add(c.recipient_id)

    posts = Post.objects.select_related('author').prefetch_related('tags').order_by('-created_at')
    if connected_user_ids:
        posts = posts.filter(author_id__in=list(connected_user_ids) + [request.user.id])
    else:
        # Fallback: show recent public posts from everyone to avoid empty feed
        posts = posts[:20]

    news_items = NewsItem.objects.all()[:8]
    jobs = Job.objects.all()[:8]
    User = get_user_model()
    connections_users = User.objects.filter(id__in=list(connected_user_ids)) if connected_user_ids else User.objects.none()

    # Annotate posts with user's reaction status
    for p in posts:
        p.my_reaction_kind = p.get_user_reaction(request.user.id)

    context = {
        'posts': posts,
        'has_connections': bool(connected_user_ids),
        'news_items': news_items,
        'jobs': jobs,
        'connections': connections_users,
    }
    return render(request, 'main.html', context)


@login_required
def network_view(request):
    incoming = Connection.objects.filter(recipient=request.user, status='pending')
    outgoing = Connection.objects.filter(sender=request.user).exclude(status='accepted')

    # Simple suggestions: users not connected and not self
    User = get_user_model()
    connected_ids = {request.user.id}
    for c in Connection.objects.filter(Q(sender=request.user) | Q(recipient=request.user), status='accepted'):
        connected_ids.add(c.sender_id)
        connected_ids.add(c.recipient_id)
    suggestions = User.objects.exclude(id__in=connected_ids)[:10]

    return render(request, 'network.html', {
        'incoming': incoming,
        'outgoing': outgoing,
        'suggestions': suggestions,
    })


@login_required
def jobs_view(request):
    return render(request, 'jobs.html', { 'jobs': Job.objects.order_by('-created_at')[:25] })


@login_required
def messaging_view(request):
    # Optional: open or create a conversation via ?user_id=
    other_user_id = request.GET.get('user_id')
    if other_user_id:
        User = get_user_model()
        other = get_object_or_404(User, id=other_user_id)
        convo = Conversation.objects.filter(participants=request.user).filter(participants=other).first()
        if not convo:
            convo = Conversation.objects.create()
            convo.participants.add(request.user, other)
        return render(request, 'messaging.html', {'active_conversation': convo})
    return render(request, 'messaging.html')


@login_required
def notifications_view(request):
    return render(request, 'notifications.html')


@login_required
def profile_view(request):
    my_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    # Annotate posts with user's reaction status
    for p in my_posts:
        p.my_reaction_kind = p.get_user_reaction(request.user.id)
    return render(request, 'profile.html', {'my_posts': my_posts})


# View another user's profile
@login_required
def user_profile_view(request, username: str):
    User = get_user_model()
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    # Annotate posts with user's reaction status
    for p in posts:
        p.my_reaction_kind = p.get_user_reaction(request.user.id)
    # Determine connection status
    conn = Connection.objects.filter(
        (Q(sender=request.user, recipient=user) | Q(sender=user, recipient=request.user))
    ).first()
    status = conn.status if conn else 'none'
    return render(request, 'user_profile.html', {'u': user, 'posts': posts, 'connection_status': status, 'connection': conn})


# Search users
@login_required
def search_view(request):
    q = request.GET.get('q', '').strip()
    User = get_user_model()
    results = []
    if q:
        results = User.objects.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        ).order_by('username')[:50]
    return render(request, 'search.html', {'q': q, 'results': results})


# Post actions from HTML (toggle react, comment, repost) then redirect back
@login_required
def post_react_view(request, post_id: int):
    if request.method != 'POST':
        return redirect('/main')
    kind = request.POST.get('kind', 'like')
    post = get_object_or_404(Post, id=post_id)
    
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
    
    return redirect(request.META.get('HTTP_REFERER', '/main'))


@login_required
def post_comment_view(request, post_id: int):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            post = get_object_or_404(Post, id=post_id)
            comment_data = {
                'id': len(post.comments) + 1,  # Simple ID generation
                'user_id': request.user.id,
                'text': text,
                'created_at': timezone.now().isoformat(),
                'replies': []
            }
            post.comments.append(comment_data)
            post.save()
    return redirect(request.META.get('HTTP_REFERER', '/main'))


@login_required
def post_reply_view(request, post_id: int):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        text = request.POST.get('text', '').strip()
        if comment_id and text:
            post = get_object_or_404(Post, id=post_id)
            # Find the comment and add reply
            for comment in post.comments:
                if comment.get('id') == int(comment_id):
                    reply_data = {
                        'user_id': request.user.id,
                        'text': text,
                        'created_at': timezone.now().isoformat()
                    }
                    comment['replies'].append(reply_data)
                    post.save()
                    break
    return redirect(request.META.get('HTTP_REFERER', '/main'))


@login_required
def post_repost_view(request, post_id: int):
    if request.method == 'POST':
        original = get_object_or_404(Post, id=post_id)
        
        # Check if user already reposted
        for repost in original.reposts:
            if repost.get('user_id') == request.user.id:
                return redirect(request.META.get('HTTP_REFERER', '/main'))
        
        # Add repost record
        repost_data = {
            'user_id': request.user.id,
            'created_at': timezone.now().isoformat()
        }
        original.reposts.append(repost_data)
        original.save()
        
        # Create new post as repost
        repost = Post.objects.create(
            author=request.user,
            text=original.text,
            media=original.media,
            visibility='public',
            repost_of=original,
        )
        repost.tags.set(original.tags.all())
    return redirect(request.META.get('HTTP_REFERER', '/main'))


@login_required
def post_send_view(request, post_id: int):
    if request.method == 'POST':
        to_user_id = request.POST.get('to_user_id')
        if to_user_id:
            User = get_user_model()
            to_user = get_object_or_404(User, id=to_user_id)
            post = get_object_or_404(Post, id=post_id)
            
            # Add share record
            share_data = {
                'user_id': request.user.id,
                'to_user_id': int(to_user_id),
                'created_at': timezone.now().isoformat()
            }
            post.shares.append(share_data)
            post.save()
            
            # find or create conversation
            convo = Conversation.objects.filter(participants=request.user).filter(participants=to_user).first()
            if not convo:
                convo = Conversation.objects.create()
                convo.participants.add(request.user, to_user)
            Message.objects.create(
                conversation=convo,
                sender=request.user,
                body={'text': f'Check this post /p/{post_id}', 'post_id': post_id},
            )
    return redirect(request.META.get('HTTP_REFERER', '/main'))


# Connection actions
@login_required
def connect_send_view(request, user_id: int):
    User = get_user_model()
    to_user = get_object_or_404(User, id=user_id)
    if to_user == request.user:
        return redirect('/network')
    Connection.objects.get_or_create(sender=request.user, recipient=to_user, defaults={'status': 'pending'})
    return redirect('/u/' + to_user.username)


@login_required
def connect_accept_view(request, pk: int):
    conn = get_object_or_404(Connection, id=pk, recipient=request.user)
    conn.status = 'accepted'
    conn.save()
    return redirect('/network')


@login_required
def connect_reject_view(request, pk: int):
    conn = get_object_or_404(Connection, id=pk, recipient=request.user)
    conn.status = 'rejected'
    conn.save()
    return redirect('/network')


# API endpoints for AJAX interactions
@login_required
def get_comments_view(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    User = get_user_model()
    
    # Get usernames for comments and replies
    comments_with_users = []
    for comment in post.comments:
        user = User.objects.get(id=comment['user_id'])
        comment_data = {
            'id': comment['id'],
            'text': comment['text'],
            'created_at': comment['created_at'],
            'username': user.username,
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'replies': []
        }
        
        for reply in comment.get('replies', []):
            reply_user = User.objects.get(id=reply['user_id'])
            reply_data = {
                'text': reply['text'],
                'created_at': reply['created_at'],
                'username': reply_user.username,
                'full_name': f"{reply_user.first_name} {reply_user.last_name}".strip() or reply_user.username,
            }
            comment_data['replies'].append(reply_data)
        
        comments_with_users.append(comment_data)
    
    return JsonResponse({'comments': comments_with_users})


