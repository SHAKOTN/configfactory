from django.contrib.contenttypes.models import ContentType
from django_filters import FilterSet, filters

from configfactory.models import (
    Component,
    Environment,
    GlobalSettings,
    LogEntry,
    User,
)


class LogEntryFilterSet(FilterSet):

    content_type = filters.ModelChoiceFilter(
        queryset=ContentType.objects.filter(
            app_label='configfactory',
            model__in=[
                Environment._meta.model_name,
                Component._meta.model_name,
                User._meta.model_name,
                GlobalSettings._meta.model_name,
            ]
        )
    )

    class Meta:
        model = LogEntry
        fields = ['user', 'content_type', 'object_id']
