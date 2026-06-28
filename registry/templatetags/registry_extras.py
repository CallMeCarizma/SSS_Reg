from django import template

register = template.Library()


@register.filter
def get_attr(obj, attr_name):
    if obj is None or not attr_name:
        return ""
    return getattr(obj, attr_name, "")


@register.filter
def dict_get(d, key):
    if not isinstance(d, dict):
        return ""
    return d.get(key, "")


@register.filter
def verification_warning(next_date):
    """Return CSS class based on days until next verification."""
    if not next_date:
        return ""
    from datetime import date
    days = (next_date - date.today()).days
    if days <= 7:
        return "warn-red"
    if days <= 15:
        return "warn-orange"
    if days <= 30:
        return "warn-yellow"
    return ""