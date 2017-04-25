from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from configfactory.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(
        max_length=32,
        blank=True,
        verbose_name=_('first name')
    )

    last_name = models.CharField(
        max_length=32,
        blank=True,
        verbose_name=_('last name')
    )

    email = models.EmailField(
        unique=True,
        verbose_name=_('email address')
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can '
                    'log into this admin site.'),
    )

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created datetime')
    )

    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self) -> str:
        if not self.first_name or not self.last_name:
            return self.email
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self) -> str:
        if self.first_name is None:
            return self.email
        return self.first_name
