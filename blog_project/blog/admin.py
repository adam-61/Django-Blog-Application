from django.contrib import admin
from django.db.models import Count, Avg
from .models import BlogPost, Comment, PostLike, CommentLike, PostRating


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'created_at',
        'comment_count',
        'like_count',
        'average_rating',
    )
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content', 'author__username')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _comment_count=Count('comments', distinct=True),
            _like_count=Count('likes', distinct=True),
            _avg_rating=Avg('ratings__rating'),
        )

    def comment_count(self, obj):
        return obj._comment_count
    comment_count.short_description = 'Comments'
    comment_count.admin_order_field = '_comment_count'

    def like_count(self, obj):
        return obj._like_count
    like_count.short_description = 'Likes'
    like_count.admin_order_field = '_like_count'

    def average_rating(self, obj):
        return round(obj._avg_rating, 2) if obj._avg_rating else '-'
    average_rating.short_description = 'Avg Rating'
    average_rating.admin_order_field = '_avg_rating'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'parent', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'post__title')


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__title')


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'created_at')
    search_fields = ('user__username',)


@admin.register(PostRating)
class PostRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'post__title')
