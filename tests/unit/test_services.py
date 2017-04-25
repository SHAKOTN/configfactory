from unittest import mock

from django.test import TestCase

from configfactory.models import Component
from configfactory.services import get_settings, generate_api_token
from configfactory.test.factories import EnvironmentFactory, UserFactory


class ServicesTestCase(TestCase):

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
        params_component_config = params_component\
            .configs\
            .get(environment__isnull=True)
        params_component_config.settings_content = """
        {
            "debug": true,
            "timezone": "UTC"
        }
        """
        params_component_config.save()

        amqp_component = Component.objects.create(
            name='AMQP',
            alias='amqp',
            is_global=False
        )
        amqp_component_config = amqp_component\
            .configs\
            .get(environment__isnull=True)
        amqp_component_config.settings_content = """
        {
            "default": {
                "url": "amqp://10.10.10.10:6789"
            }
        }
        """
        amqp_component_config.save()

        db_component = Component.objects.create(
            name='Database',
            alias='db',
            is_global=False
        )
        db_component_config = db_component\
            .configs\
            .get(environment__isnull=True)
        db_component_config.settings_content = """
        {
            "default": {
                "host": "127.0.0.1",
                "port": 5567,
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
                'timezone': 'UTC'
            },
            'amqp': {
                'default': {
                    'url': 'amqp://10.10.10.10:6789'
                }
            },
            'db': {
                'default': {
                    'host': '127.0.0.1',
                    'port': 5567,
                    'name': 'default',
                    'username': 'root',
                    'password': '123123',
                }
            }
        }

        data = get_settings()

        self.assertDictEqual(data, expected)

    def test_generate_api_token(self):

        user = UserFactory()
        user.api_token.token = 'aaa'
        user.api_token.save()

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
