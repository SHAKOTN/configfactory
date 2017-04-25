from django.db.models import Count
from django.template import Library
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import get_objects_for_user

from configfactory.models import Component, Environment, UserComponentStar

register = Library()


@register.inclusion_tag('app/layouts/tags/sidebar_menu.html')
def sidebar_menu(request):

    user = request.user

    resolver_match = request.resolver_match
    url_name = resolver_match.url_name
    pk = resolver_match.kwargs.get('pk')

    components = get_objects_for_user(
        user=user,
        perms=(
            'view_component',
        ),
        klass=Component
    ).annotate(
        has_star=Count('usercomponentstar')
    ).order_by('-has_star', 'name')

    components_stars = list(
        UserComponentStar.objects.filter(
            user=request.user,
            component__in=components
        ).values_list('component_id', flat=True)
    )

    components_items = [
        {
            'title': component.name,
            'url': reverse('component_base_settings', kwargs={
                'pk': component.pk
            }),
            'icon': 'angle-right',
            'active': url_name in [
                'component_base_settings',
                'component_env_settings',
                'delete_component',
                'update_component',
                'update_component_base_settings',
                'update_component_env_settings',
            ] and str(component.pk) == pk,
            'has_star': component.pk in components_stars
        }
        for component in components[:25]
    ]
    if components.count() > 25:
        components_items.append({
            'title': _('Show All'),
            'url': reverse('components'),
            'icon': 'angle-double-right',
            'active': url_name in [
                'components',
            ]
        })

    if user.is_staff:
        items = [
            {
                'title': _('Main menu'),
                'header': True
            },
            {
                'title': _('Components'),
                'url': reverse('components') if not components_items else None,
                'icon': 'th-large',
                'children': components_items,
                'active': url_name in [
                    'component_base_settings',
                    'component_env_settings',
                    'components',
                    'create_component',
                    'delete_component',
                    'update_component',
                    'update_component_base_settings',
                    'update_component_env_settings',
                ]
            },
            {
                'title': _('Environments'),
                'url': reverse('environments'),
                'icon': 'cloud',
                'active': url_name in [
                    'environments',
                    'create_environment',
                    'update_environment',
                    'delete_environment'
                ]
            },
            {
                'title': _('Logs'),
                'url': reverse('logs'),
                'icon': 'bars',
                'active': url_name in [
                    'logs',
                    'log_detail',
                ]
            },
            {
                'title': _('Users'),
                'url': reverse('users'),
                'icon': 'users',
                'active': url_name in [
                    'users',
                    'create_user',
                    'update_user',
                    'update_user_permissions',
                    'update_user_permissions_by_model',
                    'delete_user'
                ]
            },
            {
                'title': _('Global Settings'),
                'url': reverse('update_global_settings'),
                'icon': 'cogs',
                'active': url_name in [
                    'update_global_settings',
                ]
            },
        ]

    else:
        items = components_items

    return {
        'items': items
    }


@register.inclusion_tag('app/layouts/tags/tabs.html')
def environments_tabs(request, component, edit=False):

    user = request.user

    query_string = request.GET.urlencode()

    alias = request.resolver_match.kwargs.get('alias')

    if edit:
        base_viewname = 'update_component_base_settings'
        env_viewname = 'update_component_env_settings'
    else:
        base_viewname = 'component_base_settings'
        env_viewname = 'component_env_settings'

    items = []

    if not component.is_global:

        items = [
            {
                'title': _('Base'),
                'active': alias is None,
                'url': '{path}{qm}{query}'.format(
                    path=reverse(base_viewname, kwargs={
                        'pk': component.pk
                    }),
                    qm='?' if query_string else '',
                    query=query_string
                )
            }
        ]

        environments = Environment.objects.with_user_perms(
            user=user,
            perms=(
                'view_environment',
            ),
        )

        for environment in environments:
            items.append({
                'title': environment.name,
                'active': environment.alias == alias,
                'url': '{path}{qm}{query}'.format(
                    path=reverse(env_viewname, kwargs={
                        'pk': component.pk,
                        'alias': environment.alias
                    }),
                    qm='?' if query_string else '',
                    query=query_string
                )
            })

    return {
        'request': request,
        'items': items,
    }


@register.inclusion_tag('app/layouts/tags/tabs.html')
def account_tabs(request):

    resolver_match = request.resolver_match
    url_name = resolver_match.url_name

    items = [
        {
            'title': _('Personal'),
            'active': url_name == 'personal_info',
            'url': reverse('personal_info')
        },
        {
            'title': _('Password'),
            'active': url_name == 'password_change',
            'url': reverse('password_change')
        },
        {
            'title': _('API'),
            'active': url_name == 'api_settings',
            'url': reverse('api_settings')
        },
    ]

    return {
        'request': request,
        'items': items,
    }


@register.inclusion_tag('app/layouts/tags/tabs.html')
def permission_types_tabs(request, user):

    resolver_match = request.resolver_match
    url_name = resolver_match.url_name
    model_name = resolver_match.kwargs.get(
        'model',
        Environment._meta.model_name
    )

    items = [
        {
            'title': _('Environments'),
            'active': url_name in [
                'update_user_permissions',
                'update_user_permissions_by_model'
            ] and model_name == Environment._meta.model_name,
            'url': reverse('update_user_permissions_by_model', kwargs={
                'pk': user.pk,
                'model': Environment._meta.model_name
            })
        },
        {
            'title': _('Components'),
            'active': url_name in [
                'update_user_permissions',
                'update_user_permissions_by_model'
            ] and model_name == Component._meta.model_name,
            'url': reverse('update_user_permissions_by_model', kwargs={
                'pk': user.pk,
                'model': Component._meta.model_name
            })
        },
    ]

    return {
        'request': request,
        'items': items
    }
