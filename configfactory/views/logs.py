from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django_filters.views import FilterView

from configfactory.decorators import staff_member_required
from configfactory.filters import LogEntryFilterSet
from configfactory.models import LogEntry


@method_decorator([
    login_required,
    staff_member_required
], name='dispatch')
class LogsListView(FilterView):

    template_name = 'app/logs/list.html'

    paginate_by = 25

    filterset_class = LogEntryFilterSet

    def get_queryset(self):
        user = self.request.user
        log_entry_set = LogEntry.objects.select_related('user', 'content_type')
        if user.is_staff and not user.is_superuser:
            return log_entry_set.filter(user=user)
        return log_entry_set.all()


@method_decorator([
    login_required,
    staff_member_required
], name='dispatch')
class LogsDetailView(DetailView):

    template_name = 'app/logs/detail.html'

    def get_queryset(self):
        user = self.request.user
        log_entry_set = LogEntry.objects.select_related('user', 'content_type')
        if user.is_staff and not user.is_superuser:
            return log_entry_set.filter(user=user)
        return log_entry_set.all()
