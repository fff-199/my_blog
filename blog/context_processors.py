from .sidebar import get_sidebar_context


def sidebar_context(request):
    try:
        context = get_sidebar_context()
    except Exception:
        context = {
            "categories": [],
            "tags": [],
            "recent_posts": [],
        }

    context["q"] = request.GET.get("q", "").strip()
    return context

