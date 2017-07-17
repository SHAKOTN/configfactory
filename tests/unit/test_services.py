from unittest import mock

from django.test import TestCase

from configfactory.models import Component
from configfactory.services import get_settings, generate_api_token
from configfactory.test.factories import EnvironmentFactory, UserFactory


class ServicesTestCase(TestCase):

    maxDiff = None

    def test_get_settings_data_empty(self):

        self.assertDictEqual(
            get_settings(),
            {}
        )

    def test_get_settings_data_dev(self):

        EnvironmentFactory(
            name='Development',
            alias='development'
        )

        params_component = Component.objects.create(
            name='Parameters',
            alias='params',
            is_global=True
        )
        params_component_config = params_component.configs.base().get()
        params_component_config.settings_content = """
        {
            "debug": true,
            "timezone": "UTC",
            "default_host": "localhost",
            "default_port": 5555
        }
        """
        params_component_config.save()

        amqp_component = Component.objects.create(
            name='AMQP',
            alias='amqp',
            is_global=False
        )
        amqp_component_config = amqp_component.configs.base().get()
        amqp_component_config.settings_content = """
        {
            "default": {
                "url": "amqp://${param:params.default_host}:6789"
            }
        }
        """
        amqp_component_config.save()

        db_component = Component.objects.create(
            name='Database',
            alias='db',
            is_global=False
        )
        db_component_config = db_component.configs.base().get()
        db_component_config.settings_content = """
        {
            "default": {
                "debug": "${param:params.debug}",
                "host": "${param:params.default_host}",
                "port": "${param:params.default_port}",
                "name": "default",
                "username": "root",
                "password": "123123"
            }
        }
        """
        db_component_config.save()

        expected = {
            'params': {
                'debug': True,
                'timezone': 'UTC',
                'default_host': 'localhost',
                'default_port': 5555
            },
            'amqp': {
                'default': {
                    'url': 'amqp://localhost:6789'
                }
            },
            'db': {
                'default': {
                    'debug': True,
                    'host': 'localhost',
                    'port': 5555,
                    'name': 'default',
                    'username': 'root',
                    'password': '123123',
                }
            }
        }

        data = get_settings(inject=True)

        self.assertDictEqual(data, expected)

    def test_generate_api_token(self):

        user = UserFactory()
        user.api_token = 'aaa'
        user.save()

        with mock.patch(
            'django.utils.crypto.get_random_string',
            side_effect=[
                'aaa',
                'aaa',
                'bbb'
            ]
        ):
            token = generate_api_token()

            self.assertEqual(token, 'bbb')
