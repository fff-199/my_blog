"""
PythonAnywhere 生产环境配置
在 PythonAnywhere 上部署时使用此配置
"""
from .settings import *
import os

# 关闭调试模式
DEBUG = False

# 允许的主机 - 替换为你的 PythonAnywhere 用户名
# 例如: 'yourusername.pythonanywhere.com'
ALLOWED_HOSTS = [
    '.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# 安全设置
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)

# 静态文件设置
STATIC_ROOT = BASE_DIR / 'staticfiles'

# CSRF 信任源
CSRF_TRUSTED_ORIGINS = [
    'https://*.pythonanywhere.com',
]

# 数据库 (PythonAnywhere 免费版使用 SQLite)
# 如需使用 MySQL，取消下面的注释并配置
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'yourusername$myblog',
#         'USER': 'yourusername',
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST': 'yourusername.mysql.pythonanywhere-services.com',
#     }
# }
