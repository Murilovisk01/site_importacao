from django import template

register = template.Library()

@register.filter
def strip_spaces(value):
    if isinstance(value, str):
        return value.strip()
    return value
