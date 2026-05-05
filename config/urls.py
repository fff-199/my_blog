"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog import views as blog_views
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import CategorySitemap, PostSitemap, StaticViewSitemap, TagSitemap

sitemaps = {
    "posts": PostSitemap,
    "categories": CategorySitemap,
    "tags": TagSitemap,
    "static": StaticViewSitemap,
}

handler404 = blog_views.page_not_found
handler500 = blog_views.server_error

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("blog.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django_sitemap"),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
