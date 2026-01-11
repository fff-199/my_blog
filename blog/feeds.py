"""
RSS Feed 订阅
"""
from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Post


class LatestPostsFeed(Feed):
    """最新文章 RSS Feed"""
    title = "我的博客 - 最新文章"
    link = "/"
    description = "订阅我的博客，获取最新文章更新"

    def items(self):
        return Post.objects.filter(is_published=True).order_by('-created_at')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or item.content[:300]

    def item_link(self, item):
        return reverse('blog:post_detail', args=[item.slug])

    def item_pubdate(self, item):
        return item.created_at

    def item_author_name(self, item):
        return item.author.username
