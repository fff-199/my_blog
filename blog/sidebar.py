from django.db.models import Count, Q

from .models import Category, Post, Tag


def get_sidebar_context(*, exclude_post_id=None):
    categories = Category.objects.annotate(
        post_count=Count("posts", filter=Q(posts__is_published=True))
    )
    tags = Tag.objects.all()
    recent_posts_qs = Post.objects.filter(is_published=True)
    if exclude_post_id is not None:
        recent_posts_qs = recent_posts_qs.exclude(pk=exclude_post_id)
    recent_posts = recent_posts_qs[:5]

    return {
        "categories": categories,
        "tags": tags,
        "recent_posts": recent_posts,
    }

