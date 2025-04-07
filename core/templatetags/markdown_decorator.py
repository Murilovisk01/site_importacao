from django import template
import markdown

register = template.Library()

@register.filter
def render_markdown(texto):
    return markdown.markdown(texto, extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables'])
