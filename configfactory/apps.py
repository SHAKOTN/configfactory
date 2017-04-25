from django.apps import AppConfig
from django.db.models.signals import post_migrate

from configfactory.management import create_global_settings


class ConfigFactoryConfig(AppConfig):

    name = 'configfactory'

    label = 'configfactory'

    def ready(self):

        post_migrate.connect(create_global_settings, sender=self)

        self.module.autodiscover()
