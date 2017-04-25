from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserComponentStar(models.Model):

    user = models.ForeignKey(
        to='configfactory.User'
    )

    component = models.ForeignKey(
        to='configfactory.Component'
    )

    class Meta:
        verbose_name = _('user component star')
        verbose_name_plural = _('user component stars')
        unique_together = ('user', 'component')
