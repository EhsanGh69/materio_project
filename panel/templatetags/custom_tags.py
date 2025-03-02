from django import template

register = template.Library()

@register.filter()
def min(value, arg):
    return value - arg

@register.filter
def get_dict_value(dictionary, key):
    return dictionary.get(key, False)