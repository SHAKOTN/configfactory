from django.apps import apps as global_apps
from django.db import DEFAULT_DB_ALIAS, router

from configfactory.settings import GLOBAL_SETTINGS_DEFAULTS


def create_global_settings(verbosity=2, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):

    try:
        GlobalSettings = apps.get_model('configfactory', 'GlobalSettings')
    except LookupError:
        return

    if not router.allow_migrate_model(using, GlobalSettings):
        return

    if not GlobalSettings.objects.using(using).exists():
        if verbosity >= 2:
            print("Creating GlobalSettings object")
        GlobalSettings.objects\
            .using(using)\
            .create(**GLOBAL_SETTINGS_DEFAULTS)
