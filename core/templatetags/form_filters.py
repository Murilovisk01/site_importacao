from django import template
from django.forms.boundfield import BoundField

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    if isinstance(field, BoundField):
        return field.as_widget(attrs={"class": css_class})
    return field  # Retorna o valor original se não for campo

@register.filter
def index(sequence, i):
    try:
        return sequence[int(i)]
    except (IndexError, ValueError):
        return None
