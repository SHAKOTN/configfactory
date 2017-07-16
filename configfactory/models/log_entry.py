import dictdiffer
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from configfactory import choices, constants
from configfactory.utils import json_dumps, json_loads


class LogEntry(models.Model):

    user = models.ForeignKey(
        to='configfactory.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('user'),
    )

    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.SET_NULL,
        verbose_name=_('content type'),
        blank=True,
        null=True,
    )

    object_id = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('object id'),
    )

    object_repr = models.CharField(
        max_length=200,
        verbose_name=_('object repr')
    )

    action = models.CharField(
        max_length=64,
        choices=choices.ACTIONS,
        db_index=True,
        verbose_name=_('action')
    )

    action_time = models.DateTimeField(
        _('action time'),
        default=timezone.now,
        editable=False,
    )

    prev_data_content = models.TextField(
        blank=True,
        verbose_name=_('previous data content')
    )

    next_data_content = models.TextField(
        blank=True,
        verbose_name=_('next data content')
    )

    class Meta:
        ordering = ('-action_time',)

    def __str__(self):
        return self.message

    @property
    def prev_data(self) -> dict:
        return json_loads(self.prev_data_content)

    @prev_data.setter
    def prev_data(self, obj: dict):
        self.prev_data_content = json_dumps(obj)

    @property
    def next_data(self) -> dict:
        return json_loads(self.next_data_content)

    @next_data.setter
    def next_data(self, obj: dict):
        self.next_data_content = json_dumps(obj)

    @property
    def diff_data(self):
        return list(
            dictdiffer.diff(
                self.prev_data,
                self.next_data
            )
        )

    @property
    def message(self) -> str:

        if self.action == constants.ACTION_CREATE:
            if self.user_id and self.object_id and self.content_type_id:
                return _('%(user)s created %(object)s %(content_type)s.') % {
                    'user': self.user,
                    'object': self.object_repr,
                    'content_type': self.content_type
                }
            elif self.object_id and self.content_type_id:
                return _('%(object)s %(content_type)s '
                         'was successfully created.') % {
                    'object': self.object_repr,
                    'content_type': self.content_type
                }

        elif self.action == constants.ACTION_UPDATE:
            if self.user_id and self.object_id and self.content_type_id:
                return _('%(user)s updated %(object)s %(content_type)s.') % {
                    'user': self.user,
                    'object': self.object_repr,
                    'content_type': self.content_type
                }
            elif self.object_id and self.content_type_id:
                return _('%(object)s %(content_type)s '
                         'was successfully updated.') % {
                    'object': self.object_repr,
                    'content_type': self.content_type
                }

        elif self.action == constants.ACTION_DELETE:
            if self.user_id and self.object_repr and self.content_type_id:
                return _('%(user)s deleted %(object)s %(content_type)s.') % {
                    'user': self.user,
                    'object': self.object_repr,
                    'content_type': self.content_type
                }
            elif self.object_repr and self.content_type_id:
                return _('%(object)s %(content_type)s '
                         'was successfully deleted.') % {
                    'object': self.object_repr,
                    'content_type': self.content_type
                }

        return self.action

    def get_object(self):
        if self.content_type and self.object_id:
            return self.content_type.get_object_for_this_type(pk=self.object_id)
        return None

    def get_object_url(self):
        if self.content_type and self.object_id:
            obj = self.get_object()
            if hasattr(obj, 'get_absolute_url'):
                return obj.get_absolute_url()
        return None
