from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from configfactory.managers import EnvironmentManager


class Environment(models.Model):

    name = models.CharField(
        max_length=128,
        verbose_name=_('name'),
        unique=True
    )

    alias = models.SlugField(
        unique=True,
        verbose_name=_('alias')
    )

    order = models.SmallIntegerField(
        verbose_name=_('order'),
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('create datetime')
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('update datetime')
    )

    objects = EnvironmentManager()

    class Meta:
        verbose_name = _('environment')
        verbose_name_plural = _('environments')
        ordering = ('order', 'name',)
        permissions = (
            ('view_environment', _('Can view environment')),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('update_environment', kwargs={
            'pk': self.pk
        })
