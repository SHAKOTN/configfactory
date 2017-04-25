from django.shortcuts import resolve_url
from django.template import Library
from django.urls import NoReverseMatch
from django.utils.safestring import mark_safe

from configfactory import constants

register = Library()


@register.simple_tag
def true_false_icon(value):
    class_ = 'check text-green' if value else 'close text-red'
    return mark_safe("""
        <i class="fa fa-{}"></i>
    """.format(class_))


@register.simple_tag
def action_icon(value):
    icon_map = {
        constants.ACTION_CREATE: 'plus-circle',
        constants.ACTION_UPDATE: 'pencil',
        constants.ACTION_DELETE: 'minus-circle',
    }
    color_map = {
        constants.ACTION_CREATE: 'green',
        constants.ACTION_UPDATE: 'blue',
        constants.ACTION_DELETE: 'red',
    }
    icon = icon_map.get(value, 'info')
    color = color_map.get(value, 'aqua')
    return mark_safe("""
        <i class="fa fa-{} text-{}"></i>
    """.format(icon, color))


@register.inclusion_tag('app/layouts/shared/back_btn.html')
def back_btn(request, to, *args, **kwargs):
    try:
        default_url = resolve_url(to, *args, **kwargs)
    except NoReverseMatch:
        default_url = None
    next_url = request.GET.get('next')
    return {
        'default_url': default_url,
        'next_url': next_url
    }


@register.inclusion_tag('app/layouts/tags/pagination.html')
def pagination(page_obj, float_pos='right', pid=None, size=None):
    return {
        'page_obj': page_obj,
        'id': pid,
        'float_pos': float_pos,
        'size': size
    }
