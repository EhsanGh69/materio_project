from django import template

from utils.tools import get_codenames

register = template.Library()

@register.filter()
def min(value, arg):
    return value - arg

@register.filter
def get_dict_value(dictionary, key):
    return dictionary.get(key, False)


@register.filter
def has_role_perm(user, role):
    required_perms = get_codenames(role, app_name=True)
    return user.has_perms(required_perms)
