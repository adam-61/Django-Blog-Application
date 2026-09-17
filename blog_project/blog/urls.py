from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('my-posts/', views.my_posts, name='my_posts'),

    path(
        'comment/<int:comment_id>/delete/',
        views.delete_comment,
        name='delete_comment'
    ),
    path(
        'comment/<int:comment_id>/edit/',
        views.edit_comment,
        name='edit_comment'
    ),
    path(
        'post/<int:post_id>/comment/<int:comment_id>/reply/',
        views.add_reply,
        name='add_reply'
    ),

    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path(
        'comment/<int:comment_id>/like/',
        views.like_comment,
        name='like_comment'
    ),

    path('popular/', views.popular_posts, name='popular_posts'),
    path('advanced-queries/', views.advanced_queries, name='advanced_queries'),
    path('profile/', views.my_profile, name='my_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
]
