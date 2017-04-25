from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import model_to_dict

from configfactory.models import (
    ApiToken,
    Component,
    Config,
    Environment,
    GlobalSettings,
    JSONSchema,
    User,
)
from configfactory.services import generate_api_token
from configfactory.utils import global_settings


@receiver(post_save, sender=Environment)
def add_component_environments(instance, created, **kwargs):

    if created:

        # Create environment configurations
        for component in Component.objects.not_global():
            base_config = component.configs.base().get()
            env_config = Config(
                component=component,
                environment=instance,
                settings_content=base_config.settings_content
            )
            component.configs.add(env_config, bulk=False)


@receiver(post_save, sender=Component)
def set_component_environments(instance, created, **kwargs):

    if created:

        # Create environment configurations
        configs = [
            Config()
        ]
        if not instance.is_global:
            for environment in Environment.objects.all():
                configs.append(Config(environment=environment))
        instance.configs.set(configs, bulk=False)

        # Create JSON schema
        if instance.use_schema:
            JSONSchema.objects.get_or_create(component=instance)


@receiver(post_save, sender=GlobalSettings)
def reload_global_settings(instance, **kwargs):
    fields = model_to_dict(instance, exclude=['id'])
    for key, value in fields.items():
        global_settings[key] = value


@receiver(post_save, sender=User)
def create_user_api_token(instance, created, **kwargs):
    if created:
        api_token = ApiToken()
        api_token.user = instance
        api_token.token = generate_api_token()
        api_token.save()
