from collections import OrderedDict

from django.test import TestCase

from configfactory.models import Component, Config
from configfactory.services import get_settings
from configfactory.test.factories import EnvironmentFactory


class ComponentTestCase(TestCase):

    def test_create_component_without_environments(self):

        component = Component.objects.create(
            name='AMQP',
            alias='amqp'
        )

        self.assertEqual(component.configs.count(),  1)

        configs = component.configs.first()

        self.assertIsNone(configs.environment)

    def test_create_component(self):

        dev = EnvironmentFactory(
            name='Development',
            alias='dev'
        )

        prod = EnvironmentFactory(
            name='Production',
            alias='prod'
        )

        component = Component.objects.create(
            name='AMQP',
            alias='amqp'
        )

        self.assertEqual(component.configs.count(), 3)

        base_config = component.configs.filter(
            environment__isnull=True
        ).get()

        dev_config = component.configs.filter(
            environment__alias='dev'
        ).get()

        prod_config = component.configs.filter(
            environment__alias='prod'
        ).get()

        self.assertIsNone(base_config.environment)
        self.assertEqual(dev_config.environment.alias, dev.alias)
        self.assertEqual(prod_config.environment.alias, prod.alias)

    def test_create_global_component(self):

        EnvironmentFactory(
            name='Development',
            alias='dev'
        )

        component = Component.objects.create(
            name='AMQP',
            alias='amqp',
            is_global=True
        )

        self.assertEqual(component.configs.count(), 1)

    def test_delete_component_environment(self):

        dev = EnvironmentFactory(
            name='Development',
            alias='dev'
        )

        component = Component.objects.create(
            name='AMQP',
            alias='amqp'
        )

        self.assertEqual(component.configs.count(), 2)

        dev.delete()

        self.assertEqual(component.configs.count(), 1)


class ConfigTestCase(TestCase):

    def test_get_set_json_settings(self):

        config = Config(settings_content='{"a": 100}')

        self.assertDictEqual(
            config.settings,
            {'a': 100}
        )

        self.assertEqual(
            config.settings_json,
            '{"a": 100}'
        )

    def test_component_create_environments(self):

        EnvironmentFactory(
            name='Development',
            alias='dev'
        )

        component = Component.objects.create(
            name='AMQP',
            alias='amqp',
            is_global=False
        )

        self.assertEqual(component.configs.count(), 2)

        EnvironmentFactory(
            name='Production',
            alias='production'
        )

        self.assertEqual(component.configs.count(), 3)

    def test_component_settings(self):

        dev = EnvironmentFactory(
            name='Development',
            alias='dev'
        )

        component = Component.objects.create(
            name='AMQP',
            alias='amqp',
            is_global=False
        )

        base_config = component.configs.get(environment__isnull=True)
        base_config.settings_content = '{"a": 100, "b": {"c": 200}}'
        base_config.save()

        self.assertDictEqual(
            base_config.settings,
            OrderedDict([
                ('a', 100),
                ('b', OrderedDict([
                    ('c', 200)
                ])),
            ])
        )

        self.assertJSONEqual(
            base_config.settings_json,
            '{"a": 100, "b": {"c": 200}}'
        )

        self.assertJSONEqual(
            get_settings(base_config, raw=True),
            '{"a": 100, "b": {"c": 200}}'
        )

        self.assertJSONEqual(
            get_settings(base_config, flatten=True, raw=True),
            '{"a": 100, "b.c": 200}'
        )

        dev_config = component.configs.get(environment=dev)
        dev_config.settings_content = '{"b": {"c": 1000}}'
        dev_config.save()

        self.assertDictEqual(
            dev_config.settings,
            OrderedDict([
                ('a', 100),
                ('b', OrderedDict([
                    ('c', 1000)
                ])),
            ])
        )

        self.assertJSONEqual(
            dev_config.settings_json,
            '{"a": 100, "b": {"c": 1000}}'
        )
        self.assertJSONEqual(
            get_settings(dev_config, raw=True),
            '{"a": 100, "b": {"c": 1000}}'
        )
        self.assertJSONEqual(
            get_settings(dev_config, flatten=True, raw=True),
            '{"a": 100, "b.c": 1000}'
        )
