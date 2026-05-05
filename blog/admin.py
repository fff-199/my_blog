from django.contrib import admin
from .models import Category, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """分类管理"""
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """标签管理"""
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """文章管理"""
    list_display = ['title', 'author', 'category', 'is_published', 'views', 'created_at']
    list_filter = ['is_published', 'category', 'tags', 'created_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    # 字段分组
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        ('封面图片', {
            'fields': ('cover_image',),
            'description': '上传文章封面图片（可选）'
        }),
        ('内容', {
            'fields': ('excerpt', 'content')
        }),
        ('状态', {
            'fields': ('is_published', 'views'),
            'classes': ('collapse',)
        }),
    )
    
    # 多对多字段水平展示
    filter_horizontal = ['tags']
    
    # 批量操作
    actions = ['make_published', 'make_draft']
    
    @admin.action(description='设为已发布')
    def make_published(self, request, queryset):
        queryset.update(is_published=True)
    
    @admin.action(description='设为草稿')
    def make_draft(self, request, queryset):
        queryset.update(is_published=False)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """评论管理"""
    list_display = ['author_name', 'author_email', 'post', 'parent', 'created_at', 'is_approved']
    list_filter = ['is_approved', 'created_at', 'post']
    search_fields = ['author_name', 'author_email', 'content', 'post__title']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    # 批量操作
    actions = ['approve_comments', 'reject_comments']
    
    @admin.action(description='批准选中的评论')
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    
    @admin.action(description='拒绝选中的评论')
    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)
