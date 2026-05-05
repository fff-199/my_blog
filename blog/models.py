from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
import uuid


class Category(models.Model):
    """
    文章分类模型
    用于将文章归类到不同的主题分类下
    """
    name = models.CharField(max_length=100, verbose_name="分类名称")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL标识")
    description = models.TextField(blank=True, verbose_name="分类描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = "分类"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True) or str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:category_posts", args=[self.slug])


class Tag(models.Model):
    """
    文章标签模型
    用于给文章添加多个标签，便于分类和搜索
    """
    name = models.CharField(max_length=50, verbose_name="标签名称")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="URL标识")

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = "标签"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True) or str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:tag_posts", args=[self.slug])


class Post(models.Model):
    """
    博客文章模型
    包含文章的所有核心信息
    """
    title = models.CharField(max_length=200, verbose_name="标题")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="URL标识")
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="文章摘要")
    content = models.TextField(verbose_name="正文内容")
    
    # 关联字段
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="作者"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='posts',
        verbose_name="分类"
    )
    tags = models.ManyToManyField(
        Tag, 
        blank=True,
        related_name='posts',
        verbose_name="标签"
    )
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    # 状态字段
    is_published = models.BooleanField(default=True, verbose_name="是否发布")
    views = models.PositiveIntegerField(default=0, verbose_name="浏览次数")
    
    # 封面图片
    cover_image = models.ImageField(
        upload_to='covers/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="封面图片"
    )

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True) or str(uuid.uuid4())[:8]
        if not self.excerpt and self.content:
            self.excerpt = self.content[:200] + '...' if len(self.content) > 200 else self.content
        super().save(*args, **kwargs)

    def get_comments(self):
        return self.comments.filter(is_approved=True, parent__isnull=True).order_by('-created_at')

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[self.slug])


class Comment(models.Model):
    """
    评论模型
    支持读者对文章进行评论
    """
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name="文章"
    )
    author_name = models.CharField(max_length=100, verbose_name="评论者名称")
    author_email = models.EmailField(verbose_name="评论者邮箱")
    content = models.TextField(verbose_name="评论内容")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
        verbose_name="父评论",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")
    is_approved = models.BooleanField(default=False, verbose_name="是否审核通过")

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author_name} 评论了 《{self.post.title}》'
