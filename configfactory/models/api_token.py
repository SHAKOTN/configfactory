from django.db import models
from django.utils.translation import ugettext_lazy as _


class ApiToken(models.Model):

    user = models.OneToOneField(
        to='configfactory.User',
        verbose_name=_('api token'),
        related_name='api_token'
    )

    token = models.CharField(
        max_length=48,
        verbose_name=_('token'),
        unique=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('create datetime')
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('update datetime')
    )

    class Meta:
        verbose_name = _('api token')
        verbose_name_plural = _('api tokens')
        ordering = ('created_at',)

    def __str__(self):
        return self.token
