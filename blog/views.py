from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Count, F, Q
from django.http import HttpResponse
from django.http import JsonResponse
from django.template.loader import render_to_string
from .forms import CommentCreateForm
from .models import Post, Category, Tag, Comment
from .sidebar import get_sidebar_context


def post_list(request):
    """
    首页 - 文章列表视图
    显示所有已发布的文章，支持分页
    """
    q = request.GET.get("q", "").strip()
    posts_queryset = Post.objects.filter(is_published=True)
    if q:
        posts_queryset = posts_queryset.filter(Q(title__icontains=q) | Q(content__icontains=q))
    posts_queryset = posts_queryset.select_related("author", "category").prefetch_related("tags")
    
    # 分页，每页6篇文章
    paginator = Paginator(posts_queryset, 6)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    context = {"posts": posts, "q": q}
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """
    文章详情视图
    根据slug获取文章，增加浏览次数
    """
    post = get_object_or_404(
        Post.objects.select_related("author", "category").prefetch_related("tags"),
        slug=slug,
        is_published=True,
    )
    Post.objects.filter(pk=post.pk).update(views=F("views") + 1)
    post.refresh_from_db(fields=["views"])
    
    comments = post.get_comments().prefetch_related("replies")

    context = {
        "post": post,
        "comments": comments,
        **get_sidebar_context(exclude_post_id=post.pk),
    }
    return render(request, 'blog/post_detail.html', context)


def category_posts(request, slug):
    """
    分类文章列表视图
    显示某个分类下的所有文章
    """
    category = get_object_or_404(Category, slug=slug)
    posts_queryset = (
        Post.objects.filter(category=category, is_published=True)
        .select_related("author", "category")
        .prefetch_related("tags")
    )
    
    # 分页
    paginator = Paginator(posts_queryset, 6)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    context = {"category": category, "posts": posts}
    return render(request, 'blog/category_posts.html', context)


def tag_posts(request, slug):
    """
    标签文章列表视图
    显示带有某个标签的所有文章
    """
    tag = get_object_or_404(Tag, slug=slug)
    posts_queryset = (
        Post.objects.filter(tags=tag, is_published=True)
        .select_related("author", "category")
        .prefetch_related("tags")
    )
    
    # 分页
    paginator = Paginator(posts_queryset, 6)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    context = {"tag": tag, "posts": posts}
    return render(request, 'blog/tag_posts.html', context)


def add_comment(request, post_id):
    """
    添加评论视图
    处理评论表单提交
    """
    post = get_object_or_404(Post, pk=post_id, is_published=True)
    
    if request.method == 'POST':
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                post=post,
                author_name=form.cleaned_data["author_name"].strip(),
                author_email=form.cleaned_data["author_email"],
                content=form.cleaned_data["content"],
                is_approved=False,
            )
            messages.success(request, '评论已提交，等待审核后显示。')
        else:
            messages.error(request, '请填写完整且正确的评论信息。')
    
    return redirect('blog:post_detail', slug=post.slug)

def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def add_comment_ajax(request, post_id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "invalid_method"}, status=405)
    post = get_object_or_404(Post, pk=post_id, is_published=True)
    ip = _client_ip(request)
    rate_key = f"comment_rate:{post.pk}:{ip}"
    if ip and cache.get(rate_key):
        return JsonResponse({"ok": False, "error": "rate_limited"}, status=429)

    form = CommentCreateForm(request.POST)
    if not form.is_valid():
        errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
        return JsonResponse({"ok": False, "error": "invalid_input", "errors": errors}, status=400)

    parent = None
    parent_id = form.cleaned_data.get("parent_id")
    if parent_id:
        try:
            parent = Comment.objects.get(pk=parent_id, post=post, is_approved=True, parent__isnull=True)
        except Comment.DoesNotExist:
            parent = None
    comment = Comment.objects.create(
        post=post,
        author_name=form.cleaned_data["author_name"].strip(),
        author_email=form.cleaned_data["author_email"],
        content=form.cleaned_data["content"],
        parent=parent,
        is_approved=False,
    )
    if ip:
        cache.set(rate_key, "1", timeout=10)
    html = render_to_string(
        "blog/_comment.html",
        {"comment": comment, "pending": True},
        request=request,
    )
    return JsonResponse(
        {
            "ok": True,
            "pending": True,
            "html": html,
            "parent_id": parent.pk if parent else None,
            "comment_id": comment.pk,
        }
    )

def about(request):
    """
    关于页面视图
    """
    # 统计数据
    stats = {
        'post_count': Post.objects.filter(is_published=True).count(),
        'category_count': Category.objects.count(),
        'tag_count': Tag.objects.count(),
        'comment_count': Comment.objects.filter(is_approved=True).count(),
    }
    
    context = {"stats": stats}
    return render(request, 'blog/about.html', context)


def search(request):
    """
    搜索视图
    根据关键词搜索文章标题和内容
    """
    query = request.GET.get('q', '').strip()
    posts_queryset = Post.objects.filter(is_published=True)
    
    if query:
        posts_queryset = posts_queryset.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        )
    
    posts_queryset = posts_queryset.select_related('author', 'category').prefetch_related('tags')
    
    # 分页
    paginator = Paginator(posts_queryset, 10)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'query': query,
        'result_count': posts_queryset.count(),
    }
    return render(request, 'blog/search.html', context)


def archives(request):
    """
    归档页面视图
    按年月显示文章列表
    """
    from django.db.models.functions import TruncMonth
    
    # 按月份分组统计文章数量
    archive_dates = (
        Post.objects.filter(is_published=True)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('-month')
    )
    
    context = {
        'archive_dates': archive_dates,
    }
    return render(request, 'blog/archives.html', context)


def archive_month(request, year, month):
    """
    月度归档视图
    显示指定年月的文章
    """
    posts_queryset = (
        Post.objects.filter(
            is_published=True,
            created_at__year=year,
            created_at__month=month
        )
        .select_related('author', 'category')
        .prefetch_related('tags')
    )
    
    # 分页
    paginator = Paginator(posts_queryset, 10)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'year': year,
        'month': month,
    }
    return render(request, 'blog/archive_month.html', context)


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow:",
        "Sitemap: /sitemap.xml",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")


def page_not_found(request, exception):
    return render(request, "404.html", status=404)


def server_error(request):
    return render(request, "500.html", status=500)
