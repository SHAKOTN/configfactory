import json
import os
from collections import OrderedDict

import django

from configfactory.paths import DEFAULT_CONFIG

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configfactory.settings')
os.environ.setdefault('CONFIGFACTORY_CONFIG', DEFAULT_CONFIG)

django.setup()

from configfactory.models import Component, Config, Environment, JSONSchema

Component.objects.all().delete()
Environment.objects.all().delete()
JSONSchema.objects.all().delete()
Config.objects.all().delete()


def create_environment(name, alias, order):
    try:
        environment = Environment.objects.get(alias=alias)
    except Environment.DoesNotExist:
        environment = Environment(alias=alias)
    environment.name = name
    environment.order = order
    environment.save()
    return environment


def create_component(name, alias, is_global, use_schema):
    try:
        component = Component.objects.get(alias=alias)
    except Component.DoesNotExist:
        component = Component(alias=alias)
    component.name = name
    component.is_global = is_global
    component.use_schema = use_schema
    component.save()
    return component


def migrate():

    create_environment('Development', 'development', 1)
    create_environment('Staging', 'staging', 2)
    create_environment('Production', 'production', 3)

    with open('backup_1493035927715.json') as f:

        data = json.load(f, object_hook=OrderedDict)

        for row in data:

            component_data = row['fields']
            name = component_data['name']
            alias = component_data['alias']
            is_global = component_data['is_global']
            use_schema = component_data['require_schema']
            schema = component_data['schema']
            settings_base = component_data['settings']
            settings_development = component_data['settings_development']
            settings_staging = component_data['settings_staging']
            settings_production = component_data['settings_production']

            component = create_component(name, alias, is_global, use_schema)

            if use_schema:
                component.json_schema.schema_json = json.dumps(schema)
                component.json_schema.save()

            base_config = component.configs.get(environment__isnull=True)
            base_config.settings_json = json.dumps(settings_base)
            base_config.save()

            if not is_global:

                dev_config = component.configs.get(environment__alias='development')
                dev_config.settings_json = json.dumps(settings_development)
                dev_config.save()

                stag_config = component.configs.get(environment__alias='staging')
                stag_config.settings_json = json.dumps(settings_staging)
                stag_config.save()

                prod_config = component.configs.get(environment__alias='production')
                prod_config.settings_json = json.dumps(settings_production)
                prod_config.save()

# Start migration
migrate()
