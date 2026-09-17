from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum, Min, Max
from .forms import (
    RegisterForm,
    BlogPostForm,
    CommentForm,
    ReplyForm,
    RatingForm,
)
from .models import BlogPost, Comment, PostLike, CommentLike, PostRating


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Account created successfully! You can now login.'
            )
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {
        'form': form
    })


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('home')
        else:
            return render(request, 'registration/login.html', {
                'error': 'Invalid username or password.'
            })

    return render(request, 'registration/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def home(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    posts = BlogPost.objects.select_related('author').annotate(
        comment_count=Count('comments', distinct=True),
        like_count=Count('likes', distinct=True),
        avg_rating=Avg('ratings__rating'),
    ).order_by('-created_at')

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(category__icontains=query)
        )

    if category:
        posts = posts.filter(category__icontains=category)

    return render(request, 'blog/home.html', {
        'posts': posts,
        'query': query,
        'category': category,
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            messages.success(request, 'Post created successfully!')
            return redirect('home')
    else:
        form = BlogPostForm()

    return render(request, 'blog/create_post.html', {
        'form': form
    })


def _build_comment_tree(post):

    all_comments = post.comments.select_related('author').annotate(
        like_count=Count('likes', distinct=True)
    ).order_by('created_at')

    comments_by_parent = {}

    for comment in all_comments:
        comments_by_parent.setdefault(comment.parent_id, []).append(comment)

    def attach_children(comment_list):
        for comment in comment_list:
            comment.child_list = comments_by_parent.get(comment.id, [])
            attach_children(comment.child_list)

    top_level = comments_by_parent.get(None, [])
    attach_children(top_level)

    return top_level


def post_detail(request, post_id):
    post = get_object_or_404(
        BlogPost.objects.select_related('author'),
        id=post_id
    )

    comment_form = CommentForm()
    rating_form = RatingForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        action = request.POST.get('action')

        if action == 'comment':
            comment_form = CommentForm(request.POST)

            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()

                messages.success(request, 'Comment added successfully!')
                return redirect('post_detail', post_id=post.id)

        elif action == 'rating':
            rating_form = RatingForm(request.POST)

            if rating_form.is_valid():
                PostRating.objects.update_or_create(
                    post=post,
                    user=request.user,
                    defaults={'rating': rating_form.cleaned_data['rating']}
                )

                messages.success(request, 'Your rating has been saved!')
                return redirect('post_detail', post_id=post.id)

    comments = _build_comment_tree(post)

    like_count = post.likes.count()
    user_liked = False
    user_rating = None

    rating_stats = post.ratings.aggregate(
        average=Avg('rating'),
        total=Count('id')
    )

    if request.user.is_authenticated:
        user_liked = post.likes.filter(user=request.user).exists()
        user_rating = post.ratings.filter(user=request.user).first()

        if user_rating and request.method != 'POST':
            rating_form = RatingForm(instance=user_rating)

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'form': comment_form,
        'reply_form': ReplyForm(),
        'rating_form': rating_form,
        'comments': comments,
        'like_count': like_count,
        'user_liked': user_liked,
        'average_rating': rating_stats['average'],
        'total_ratings': rating_stats['total'],
        'user_rating': user_rating,
    })


@login_required
def add_reply(request, post_id, comment_id):
    post = get_object_or_404(BlogPost, id=post_id)
    parent_comment = get_object_or_404(Comment, id=comment_id, post=post)

    if request.method == 'POST':
        form = ReplyForm(request.POST)

        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.author = request.user
            reply.parent = parent_comment
            reply.save()

            messages.success(request, 'Reply added successfully!')

    return redirect('post_detail', post_id=post.id)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)

    if post.author != request.user:
        return redirect('home')

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = BlogPostForm(instance=post)

    return render(request, 'blog/edit_post.html', {
        'form': form,
        'post': post
    })


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)

    if post.author != request.user:
        return redirect('home')

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('home')

    return render(request, 'blog/delete_post.html', {
        'post': post
    })


@login_required
def my_posts(request):
    posts = BlogPost.objects.filter(
        author=request.user
    ).select_related('author').prefetch_related(
        'comments__author',
        'likes__user',
        'ratings__user',
    ).annotate(
        comment_count=Count('comments', distinct=True),
        like_count=Count('likes', distinct=True),
        avg_rating=Avg('ratings__rating'),
    ).order_by('-created_at')

    return render(request, 'blog/my_posts.html', {
        'posts': posts
    })


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        return redirect('post_detail', post_id=comment.post.id)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('post_detail', post_id=comment.post.id)

    return redirect('post_detail', post_id=comment.post.id)


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        return redirect('post_detail', post_id=comment.post.id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated successfully!')
            return redirect('post_detail', post_id=comment.post.id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/edit_comment.html', {
        'form': form,
        'comment': comment
    })


@login_required
def like_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)

    like = PostLike.objects.filter(
        post=post,
        user=request.user
    ).first()

    if like:
        like.delete()
        messages.success(request, 'Post unliked!')
    else:
        PostLike.objects.create(
            post=post,
            user=request.user
        )
        messages.success(request, 'Post liked!')

    return redirect('post_detail', post_id=post.id)


@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    like = CommentLike.objects.filter(
        comment=comment,
        user=request.user
    ).first()

    if like:
        like.delete()
        messages.success(request, 'Comment unliked!')
    else:
        CommentLike.objects.create(
            comment=comment,
            user=request.user
        )
        messages.success(request, 'Comment liked!')

    return redirect('post_detail', post_id=comment.post.id)


def popular_posts(request):
    posts = BlogPost.objects.select_related('author').annotate(
        like_count=Count('likes', distinct=True),
        comment_count=Count('comments', distinct=True),
        avg_rating=Avg('ratings__rating'),
    ).order_by('-like_count', '-comment_count', '-avg_rating')[:10]

    return render(request, 'blog/popular_posts.html', {
        'posts': posts
    })


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.select_related('author').annotate(
        comment_count=Count('comments', distinct=True),
        like_count=Count('likes', distinct=True),
    ).order_by('-created_at')

    stats = {
        'post_count': profile_user.posts.count(),
        'comment_count': profile_user.comments.count(),
        'likes_given': (
            profile_user.post_likes.count()
            + profile_user.comment_likes.count()
        ),
        'ratings_given': profile_user.ratings_given.count(),
    }

    engagement = profile_user.posts.annotate(
        like_count=Count('likes', distinct=True)
    ).aggregate(
        total_likes_received=Sum('like_count'),
        first_post_date=Min('created_at'),
        latest_post_date=Max('created_at'),
    )

    stats['likes_received'] = engagement['total_likes_received'] or 0
    stats['first_post_date'] = engagement['first_post_date']
    stats['latest_post_date'] = engagement['latest_post_date']

    return render(request, 'blog/profile.html', {
        'profile_user': profile_user,
        'stats': stats,
        'posts': posts,
    })


@login_required
def my_profile(request):
    return profile(request, request.user.username)


def advanced_queries(request):
    author_username = request.GET.get('author', '').strip()
    keyword = request.GET.get('keyword', '').strip()
    min_likes = request.GET.get('min_likes', '1')
    min_rating = request.GET.get('min_rating', '4')
    min_comments = request.GET.get('min_comments', '0')

    min_likes = int(min_likes) if min_likes.isdigit() else 1
    min_comments = int(min_comments) if min_comments.isdigit() else 0

    try:
        min_rating = float(min_rating)
    except ValueError:
        min_rating = 4.0


    posts_by_author = BlogPost.objects.none()
    if author_username:
        posts_by_author = BlogPost.objects.filter(
            author__username=author_username
        ).select_related('author')


    posts_with_keyword = BlogPost.objects.none()
    if keyword:
        posts_with_keyword = BlogPost.objects.filter(
            Q(title__icontains=keyword) | Q(content__icontains=keyword)
        ).select_related('author')

    posts_min_likes = BlogPost.objects.select_related('author').annotate(
        like_total=Count('likes', distinct=True)
    ).filter(like_total__gte=min_likes).order_by('-like_total')


    posts_min_rating = BlogPost.objects.select_related('author').annotate(
        avg_rating=Avg('ratings__rating')
    ).filter(avg_rating__gte=min_rating).order_by('-avg_rating')


    posts_min_comments = BlogPost.objects.select_related('author').annotate(
        comment_total=Count('comments', distinct=True)
    ).filter(comment_total__gt=min_comments).order_by('-comment_total')

    posts_with_matching_commenters = BlogPost.objects.filter(
        comments__author__username__icontains='a'
    ).select_related('author').distinct()

    context = {
        'author_username': author_username,
        'keyword': keyword,
        'min_likes': min_likes,
        'min_rating': min_rating,
        'min_comments': min_comments,
        'posts_by_author': posts_by_author,
        'posts_with_keyword': posts_with_keyword,
        'posts_min_likes': posts_min_likes,
        'posts_min_rating': posts_min_rating,
        'posts_min_comments': posts_min_comments,
        'posts_with_matching_commenters': posts_with_matching_commenters,
    }

    return render(request, 'blog/advanced_queries.html', context)
