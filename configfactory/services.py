from collections import OrderedDict
from typing import Union, Optional

import dictdiffer
import jsonschema
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Model
from django.utils.translation import ugettext_lazy as _

from configfactory import constants
from configfactory.exceptions import (
    ComponentDeleteError,
    ConfigUpdateError,
    InjectKeyError,
)
from configfactory.models import (
    Component,
    Config,
    Environment,
    JSONSchema,
    LogEntry,
    User,
    UserComponentStar,
)
from configfactory.utils import (
    cleanse_dict,
    flatten_dict,
    global_settings,
    inject_params,
    json_dumps,
    json_loads,
    model_to_dict,
)


def get_settings(
        config: Config = None,
        environment: Environment = None,
        user: User = None,
        flatten: bool = False,
        secure: bool = False,
        inject: bool = False,
        raw: bool = False
) -> Union[str, OrderedDict]:

    if config:
        data = config.settings
        environment = config.environment
    else:
        data = get_all_settings(
            environment=environment,
            user=user
        )

    # Secure settings values
    if secure:
        data = cleanse_dict(
            d=data,
            hidden=global_settings['cleansed_hidden'],
            substitute=global_settings['cleansed_substitute']
        )

    # Flatten settings keys
    if flatten:
        data = flatten_dict(data)

    # Dump as json string
    json_content = json_dumps(
        obj=data,
        indent=global_settings['indent']
    )

    # Inject global settings values
    if inject:
        params = get_all_settings(environment)
        json_content = inject_params(
            content=json_content,
            params=flatten_dict(params),
            raise_exception=global_settings['inject_validation']
        )

    # Return as string
    if raw:
        return json_content

    # Return as dict
    return json_loads(json_content)


def get_config_settings(
        config: Config,
        user: User = None,
        flatten: bool = False,
        secure: bool = False,
        inject: bool = False,
        raw: bool = False
) -> Union[str, OrderedDict]:
    return get_settings(
        config=config,
        user=user,
        flatten=flatten,
        secure=secure,
        inject=inject,
        raw=raw
    )


def get_all_settings(environment: Environment = None,
                     user: User = None) -> OrderedDict:

    component_ids = None
    if user:
        component_ids = list(
            Component.objects.with_user_perms(
                user=user,
                perms=(
                    'view_component',
                )
            ).values_list(flat=True)
        )

    configs = (
        Config.objects
        .select_related('component')
        .filter(environment=environment)
    )

    if component_ids is not None:
        configs = configs.filter(component_id__in=component_ids)

    ret = OrderedDict()
    base_configs = {}

    if environment:

        base_configs = (
            Config.objects
            .select_related('component')
            .base()
        )
        if component_ids is not None:
            base_configs = base_configs.filter(component_id__in=component_ids)

        configs |= base_configs.global_()

        base_configs = {
            config.component_id: config
            for config in base_configs
        }

    for config in configs:
        config.base = base_configs.get(config.component_id)
        ret[config.component.alias] = config.settings

    return ret


def delete_component(component: Component):

    with transaction.atomic():

        environments = [None]

        if not component.is_global:
            for environment in Environment.objects.all():
                environments.append(environment)

        component.delete()

        for environment in environments:
            try:
                get_settings(
                    environment=environment,
                    inject=True,
                    raw=True
                )
            except InjectKeyError as e:
                raise ComponentDeleteError(
                    _('One of other components is referring '
                      'to `%(key)s` key.') % {
                        'key': e.key
                    }
                )


def update_config(config: Config,
                  settings_json: str,
                  commit: bool = True) -> Config:

    # Set settings
    config.settings_json = settings_json

    component = config.component

    if component.use_schema:
        json_schema, created = JSONSchema.objects.get_or_create(
            component=component
        )

        try:
            jsonschema.validate(
                instance=config.settings,
                schema=json_schema.schema
            )
        except jsonschema.ValidationError as e:
            raise ConfigUpdateError(
                _('Invalid settings schema: %(msg)s') % {
                    'msg': str(e)
                }
            )

    if not component.is_global and config.environment_id:

        base_config = component.configs.base().get()

        diff = dictdiffer.diff(
            base_config.settings,
            config.settings,
        )

        for summary in diff:
            if 'add' in summary:
                keys = ', '.join([
                    add[0] for add in summary[2]
                ])
                raise ConfigUpdateError(
                    _('Cannot add parent keys to environment configuration. '
                      'New key(s): <b>%(keys)s</b>.') % {
                        'keys': keys
                    }
                )

    with transaction.atomic():

        sid = transaction.savepoint()

        config.save()

        try:
            get_settings(
                environment=config.environment,
                inject=True,
                raw=True
            )
        except InjectKeyError as e:
            if e.key.startswith(config.component.alias):
                message = (
                    _('One of other components is referring '
                      'to `%(key)s` key.') % {
                        'key': e.key
                    }
                )
            else:
                message = e.message
            raise ConfigUpdateError(message)
        except Exception as e:
            raise ConfigUpdateError(str(e))

        if commit:
            transaction.savepoint_commit(sid)
        else:
            transaction.savepoint_rollback(sid)

    return config


def duplicate_environment(environment: Environment,
                          name: str,
                          alias: str):
    new_environment = Environment()
    new_environment.name = name
    new_environment.alias = alias
    new_environment.save()


def generate_api_token() -> str:
    from django.utils.crypto import get_random_string
    while True:
        token = get_random_string(48)
        if not User.objects.filter(api_token=token).exists():
            return token


def get_api_user(user: User) -> Optional[User]:
    if user.is_apiuser or user.is_superuser:
        return user
    if user.api_user_id:
        return user.api_user
    return None


def get_api_token(user: User) -> str:
    api_user = get_api_user(user)
    if api_user is None:
        return ''
    if not api_user.api_token:
        api_user.api_token = generate_api_token()
        api_user.save()
    return api_user.api_token


def add_component_star(user: User, component: Component) -> bool:
    if not UserComponentStar.objects.filter(
            user=user,
            component=component
    ).exists():
        star = UserComponentStar()
        star.user = user
        star.component = component
        star.save()
        return True
    return False


def remove_component_star(user: User, component: Component) -> bool:
    try:
        star = UserComponentStar.objects.get(
            user=user,
            component=component
        )
        star.delete()
        return True
    except UserComponentStar.DoesNotExist:
        return False


def log_action(action: str,
               user: User = None,
               instance: Model = None,
               object_repr: str = None,
               prev_data: dict = None,
               next_data: dict = None):

    if prev_data is None:
        prev_data = {}

    if next_data is None:
        next_data = {}

    content_type = None
    object_id = None

    if instance:
        content_type = ContentType.objects.get_for_model(instance)
        object_id = instance.pk
        if object_repr is None:
            object_repr = str(instance)

    log = LogEntry()
    log.action = action
    log.user = user
    log.content_type = content_type
    log.object_id = object_id
    log.object_repr = object_repr
    log.prev_data = prev_data
    log.next_data = next_data
    log.save()


def log_create_object(instance: Model,
                      user: User = None,
                      fields=None,
                      exclude=None):
    log_action(
        action=constants.ACTION_CREATE,
        user=user,
        instance=instance,
        next_data=model_to_dict(
            instance=instance,
            fields=fields,
            exclude=exclude
        )
    )


def log_update_object(obj: Model,
                      user: User,
                      object_repr: str = None,
                      prev_data: dict = None,
                      fields=None,
                      exclude=None):
    log_action(
        action=constants.ACTION_UPDATE,
        user=user,
        instance=obj,
        object_repr=object_repr,
        prev_data=prev_data,
        next_data=model_to_dict(
            instance=obj,
            fields=fields,
            exclude=exclude
        )
    )


def log_delete_object(obj: Model, user: User):
    log_action(
        action=constants.ACTION_DELETE,
        user=user,
        instance=obj,
        prev_data=model_to_dict(obj),
    )
