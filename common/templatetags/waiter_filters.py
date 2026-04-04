from django import template

register = template.Library()


@register.filter
def format_currency(value):
    try:
        return f"₹{float(value):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


@register.filter
def item_icon(menu_type):
    if menu_type == "VEG":
        return '<span class="text-success me-2" title="Vegetarian"><i class="fas fa-leaf"></i></span>'
    return '<span class="text-danger me-2" title="Non-Vegetarian"><i class="fas fa-drumstick-bite"></i></span>'


@register.filter
def badge_class(status):
    return {
        "PENDING": "info",
        "ACCEPTED": "success",
        "REJECTED": "danger",
        "MAKING": "warning",
        "COMPLETED": "primary",
    }.get(status, "secondary")


@register.filter
def title_case(value):
    return value.replace("_", " ").title() if value else ""
