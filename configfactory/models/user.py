from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from configfactory.managers import UserManager


class User(AbstractUser):

    api_user = models.ForeignKey(
        to='self',
        blank=True,
        null=True,
        related_name='users',
        verbose_name=_('API user'),
        help_text=_('User with API access.'),
    )

    api_token = models.CharField(
        max_length=48,
        verbose_name=_('API token'),
        blank=True,
        null=True,
        unique=True
    )

    is_apiuser = models.BooleanField(
        default=False,
        verbose_name=_('API user status'),
        help_text=_(
            'Designates whether the user can call API.'
        ),
    )

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @cached_property
    def has_api_access(self):
        return (
            self.is_apiuser
            or self.is_superuser
            or self.api_user_id is not None
        )
