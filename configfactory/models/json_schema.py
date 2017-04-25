from collections import OrderedDict

from django.db import models
from django.utils.translation import ugettext_lazy as _

from configfactory.managers import ConfigManager
from configfactory.utils import json_loads


class JSONSchema(models.Model):

    component = models.OneToOneField(
        to='configfactory.Component',
        related_name='json_schema'
    )

    content = models.TextField(default='{}', serialize=False)

    objects = ConfigManager()

    class Meta:
        verbose_name = _('JSON schema')
        verbose_name_plural = _('JSON schemas')
        permissions = (
            ('view_json_schema', _('Can view JSON schema')),
        )

    @property
    def schema(self) -> OrderedDict:
        return json_loads(self.content)

    @property
    def schema_json(self) -> str:
        return self.content

    @schema_json.setter
    def schema_json(self, value):
        self.content = value

    def to_dict(self):
        return {
            'id': self.pk,
            'schema': self.schema
        }
