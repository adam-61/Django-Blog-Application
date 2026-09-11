from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .forms import RegisterForm, BlogPostForm
from .models import BlogPost


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

    posts = BlogPost.objects.all().order_by('-created_at')

    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(category__icontains=query)
        )

    return render(request, 'blog/home.html', {
        'posts': posts,
        'query': query
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


def post_detail(request, post_id):
    post = BlogPost.objects.get(id=post_id)

    return render(request, 'blog/post_detail.html', {
        'post': post
    })


@login_required
def edit_post(request, post_id):
    post = BlogPost.objects.get(id=post_id)

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
    post = BlogPost.objects.get(id=post_id)

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
    ).order_by('-created_at')

    return render(request, 'blog/my_posts.html', {
        'posts': posts
    })