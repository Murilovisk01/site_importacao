from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter
def index(sequence, i):
    try:
        return sequence[int(i)]
    except (IndexError, ValueError):
        return None
