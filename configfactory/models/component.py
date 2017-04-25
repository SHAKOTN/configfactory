from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from configfactory.managers import ComponentManager


class Component(models.Model):

    name = models.CharField(
        max_length=128,
        verbose_name=_('name'),
        unique=True
    )

    alias = models.SlugField(
        unique=True,
        verbose_name=_('alias')
    )

    is_global = models.BooleanField(
        default=False,
        verbose_name=_('is global?'),
        help_text=_('Does not require environment settings.')
    )

    use_schema = models.BooleanField(
        default=False,
        verbose_name=_('use JSON schema?'),
        help_text=_('Use JSON schema for settings validation.')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('create datetime')
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('update datetime')
    )

    objects = ComponentManager()

    class Meta:
        verbose_name = _('component')
        verbose_name_plural = _('components')
        ordering = ('name',)
        permissions = (
            ('view_component', _('Can view component')),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('update_component', kwargs={
            'pk': self.pk
        })
