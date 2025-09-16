from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static

register = template.Library()

# Mapping size codes to image filenames
SIZE_MAP = {
    "S": "small.png",
    "M": "medium.png",
    "L": "large.png",  # default if size is not recognized
}

@register.simple_tag
def size_image(size: str, alt: str = "", base: str = "catalog/img/sml/"):
    """
    Render an <img> element for a given size code (S/M/L).

    Args:
        size (str): size code, expected values: "S", "M", "L"
        alt (str): alt text for the image (default: empty string)
        base (str): base path for the image files relative to STATIC (default: "catalog/img/sml/")

    Returns:
        str: safe HTML string containing the <img> element
    """
    filename = SIZE_MAP.get((size or "").upper(), SIZE_MAP["L"])
    url = static(base + filename)
    html = f'<img src="{url}" alt="{alt}">'
    return mark_safe(html)
