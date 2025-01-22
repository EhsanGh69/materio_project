from django import template

register = template.Library()

@register.filter()
def min(value, arg):
    return value - arg