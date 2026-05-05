from django.urls import path
from . import views
from .feeds import LatestPostsFeed

app_name = 'blog'

urlpatterns = [
    # 首页 - 文章列表
    path('', views.post_list, name='post_list'),
    
    # 搜索
    path('search/', views.search, name='search'),
    
    # 归档
    path('archives/', views.archives, name='archives'),
    path('archives/<int:year>/<int:month>/', views.archive_month, name='archive_month'),
    
    # RSS 订阅
    path('feed/', LatestPostsFeed(), name='feed'),
    
    # 关于页面
    path('about/', views.about, name='about'),
    
    # robots.txt
    path('robots.txt', views.robots_txt, name='robots_txt'),
    
    # 分类文章列表
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    
    # 标签文章列表
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    
    # 文章详情
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    
    # 添加评论
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/comment/ajax/', views.add_comment_ajax, name='add_comment_ajax'),
]
