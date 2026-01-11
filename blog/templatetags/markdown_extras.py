"""
Markdown 模板过滤器
将 Markdown 文本转换为带语法高亮的 HTML
"""
import markdown
import bleach
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='markdown')
def markdown_format(text):
    """
    将 Markdown 文本转换为 HTML
    支持代码高亮、表格、删除线等扩展
    """
    if not text:
        return ''
    
    # 配置 Markdown 扩展
    extensions = [
        'markdown.extensions.fenced_code',  # 代码块 ```
        'markdown.extensions.codehilite',   # 代码高亮
        'markdown.extensions.tables',       # 表格
        'markdown.extensions.toc',          # 目录
        'markdown.extensions.nl2br',        # 换行转 <br>
        'markdown.extensions.sane_lists',   # 更好的列表处理
    ]
    
    # 代码高亮配置
    extension_configs = {
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',
            'linenums': False,
            'guess_lang': True,
        }
    }
    
    # 转换 Markdown 为 HTML
    md = markdown.Markdown(extensions=extensions, extension_configs=extension_configs)
    html = md.convert(text)

    allowed_tags = [
        "a",
        "abbr",
        "b",
        "blockquote",
        "br",
        "code",
        "div",
        "em",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "hr",
        "i",
        "img",
        "li",
        "ol",
        "p",
        "pre",
        "span",
        "strong",
        "table",
        "tbody",
        "td",
        "th",
        "thead",
        "tr",
        "ul",
    ]
    allowed_attributes = {
        "*": ["class", "id"],
        "a": ["href", "title", "rel"],
        "img": ["src", "alt", "title"],
    }
    allowed_protocols = ["http", "https", "mailto"]

    cleaned = bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols=allowed_protocols,
        strip=True,
    )
    return mark_safe(cleaned)
