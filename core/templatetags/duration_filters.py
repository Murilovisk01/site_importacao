from django import template

register = template.Library()

@register.filter
def format_duration(value):
    if not value:
        return "00:00"
    
    total_seconds = int(value.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"
