from collections import OrderedDict

from django.test import TestCase

from configfactory.models import GlobalSettings
from configfactory.utils import (
    CircularInjectError,
    cleanse_dict,
    cleanse_value,
    global_settings,
    inject_params,
)


class UtilsTestCase(TestCase):

    def test_cleanse_value(self):

        hidden = ['password', 'secret']
        substitute = '***'

        self.assertEqual(
            cleanse_value(
                key='password',
                value='123123',
                hidden=hidden,
                substitute=substitute
            ),
            '***'
        )

        self.assertEqual(
            cleanse_value(
                key='secret',
                value='123123',
                hidden=hidden,
                substitute=substitute
            ),
            '***'
        )

        self.assertEqual(
            cleanse_value(
                key='public',
                value='123123',
                hidden=hidden,
                substitute=substitute
            ),
            '123123'
        )

        self.assertDictEqual(
            cleanse_value(
                key='private',
                value=OrderedDict([
                    ('password', 'secret')
                ]),
                hidden=hidden,
                substitute=substitute
            ),
            {
                'password': '***'
            }
        )

        self.assertDictEqual(
            cleanse_value(
                key='private',
                value=OrderedDict([
                    ('password', OrderedDict([
                        ('name', '123123')
                    ]))
                ]),
                hidden=hidden,
                substitute=substitute
            ),
            {
                'password': '***'
            }
        )

    def test_cleanse_dict(self):

        hidden = ['password', 'secret']
        substitute = '***'

        self.assertDictEqual(
            cleanse_dict(
                d={
                    'password': '123123',
                    'private': {
                        'param1': '111',
                        'secret': {
                            'word': 'please',
                            'secret': 'qwerty'
                        }
                    }
                },
                hidden=hidden,
                substitute=substitute
            ),
            {
                'password': '***',
                'private': {
                    'param1': '111',
                    'secret': {
                        'word': 'please',
                        'secret': '***'
                    }
                }
            }
        )

    def test_default_global_settings(self):

        global_values = GlobalSettings.objects.get()

        self.assertEqual(
            global_settings['indent'],
            global_values.indent
        )
        self.assertEqual(
            global_settings['cleansed_hidden'],
            global_values.cleansed_hidden
        )
        self.assertEqual(
            global_settings['cleansed_substitute'],
            global_values.cleansed_substitute
        )

        global_values.indent = 2
        global_values.cleansed_hidden = '***'
        global_values.save()

        self.assertEqual(global_settings['indent'], 2)
        self.assertEqual(global_settings['cleansed_hidden'], '***')

    def test_inject_param(self):

        content = "a = ${param:a}"

        self.assertEqual(
            inject_params(content, params={
                'a': 'TEST'
            }),
            "a = TEST"
        )

    def test_inject_params(self):

        content = "a.b.c = ${param:a.b.c}, b.c = ${param:b.c}, " \
                  "c.d.e = ${param:c.d.e}"

        self.assertEqual(
            inject_params(content, params={
                'a.b.c': 'ABC',
                'b.c': '${param:a.b.c}:BC',
                'c.d': 'CD',
                'c.d.e': '${param:b.c}:${param:c.d}',
            }),
            "a.b.c = ABC, b.c = ABC:BC, c.d.e = ABC:BC:CD"
        )

    def test_inject_params_to_self_component(self):

        content = "db.host = ${param:db.host}, " \
                  "db.default.host = ${param:db.host}"

        self.assertEqual(
            inject_params(content, params={
                'db.host': 'localhost',
                'db.default.host': '${param:db.host}',
            }),
            "db.host = localhost, db.default.host = localhost"
        )

    def test_inject_params_to_each_other(self):

        content = "a.a = ${param:a.a}, a.b = ${param:a.b}, " \
                  "b.a = ${param:b.a}, b.b = ${param:b.b}"

        self.assertEqual(
            inject_params(content, params={
                'a.a': 'AA',
                'a.b': '${param:b.b}',
                'b.a': '${param:a.b}',
                'b.b': 'BB',
            }),
            'a.a = AA, a.b = BB, b.a = BB, b.b = BB'
        )

    def test_circular_inject_params(self):

        content = "a.a = ${param:a.a}, " \
                  "b.a = ${param:b.a}"

        with self.assertRaises(CircularInjectError):
            inject_params(content, params={
                'a.a': '${param:b.a}',
                'b.a': '${param:a.a}',
            })

    def test_circular_inject_params_to_self(self):

        content = "a.a = ${param:a.a}"

        with self.assertRaises(CircularInjectError):
            inject_params(content, params={
                'a.a': '${param:a.a}',
            })
