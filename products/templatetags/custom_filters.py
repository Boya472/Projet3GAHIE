from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Sépare une chaîne selon un séparateur."""
    return value.split(arg)
