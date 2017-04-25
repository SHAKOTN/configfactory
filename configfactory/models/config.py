from collections import OrderedDict

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from configfactory.managers import ConfigManager
from configfactory.utils import json_dumps, json_loads, merge_dict


class Config(models.Model):

    environment = models.ForeignKey(
        to='configfactory.Environment',
        blank=True,
        null=True,
        related_name='configs',
    )

    component = models.ForeignKey(
        to='configfactory.Component',
        related_name='configs'
    )

    settings_content = models.TextField(default='{}', serialize=False)

    objects = ConfigManager()

    class Meta:
        unique_together = ('environment', 'component')
        ordering = ('component__alias',)
        permissions = (
            ('view_config', _('Can view config')),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._base = None

    @property
    def settings_dict(self) -> OrderedDict:
        return json_loads(self.settings_content)

    @property
    def settings(self) -> OrderedDict:
        settings_dict = self.settings_dict
        if self.environment_id:
            base_settings_dict = self.base.settings_dict
            return merge_dict(
                base_settings_dict,
                settings_dict
            )
        return settings_dict

    @property
    def settings_json(self) -> str:
        return json_dumps(self.settings)

    @settings_json.setter
    def settings_json(self, value):
        self.settings_content = value

    @property
    def base(self):
        if self.pk and self.environment_id and self._base is None:
            self._base = self.component.configs.base().get()
        return self._base

    @base.setter
    def base(self, value):
        self._base = value

    def get_absolute_url(self):
        if self.environment_id:
            return reverse('component_env_settings', kwargs={
                'pk': self.component_id,
                'alias': self.environment.alias
            })
        else:
            return reverse('component_base_settings', kwargs={
                'pk': self.component_id
            })

    def to_dict(self):
        return {
            'id': self.pk,
            'settings': self.settings
        }
