from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class GlobalSettings(models.Model):

    indent = models.SmallIntegerField(
        help_text=_('JSON indent level.')
    )

    cleansed_hidden = models.TextField(
        help_text=_('Key names that will be substituted by '
                    '`cleansed_substitute` value.')
    )

    cleansed_substitute = models.CharField(
        max_length=32,
        help_text=_('Cleansed substitute value.')
    )

    inject_validation = models.BooleanField(
        default=True,
        help_text=_('Validate injection parameters.')
    )

    def __str__(self):
        return 'Global settings'

    def get_absolute_url(self):
        return reverse('update_global_settings')
