from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from configfactory.decorators import staff_member_required
from configfactory.models import Environment
from configfactory.services import (
    log_create_object,
    log_delete_object,
    log_update_object,
)
from configfactory.shortcuts import assign_default_perms, get_all_permissions


@method_decorator([
    login_required,
    staff_member_required
], name='dispatch')
class EnvironmentsListView(ListView):

    template_name = 'app/environments/list.html'

    context_object_name = 'environments'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._queryset = None

    def get(self, request, *args, **kwargs):
        if not self.get_queryset().exists():
            return redirect('create_environment')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Environment.objects.with_user_perms(
            user=self.request.user,
            perms=(
                'view_environment',
            )
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data()

        environments_perms = get_all_permissions(
            user=self.request.user,
            object_list=context['object_list']
        )

        context.update({
            'environments_perms': environments_perms
        })

        return context


@method_decorator([
    login_required,
    staff_member_required
], name='dispatch')
class EnvironmentsCreateView(CreateView):

    template_name = 'app/environments/create.html'

    queryset = Environment.objects.all()

    fields = ('name', 'alias', 'order')

    success_url = reverse_lazy('environments')

    def form_valid(self, form):

        response = super().form_valid(form)

        user = self.request.user

        if not user.is_superuser:
            assign_default_perms(user, self.object)

        log_create_object(
            instance=self.object,
            user=user
        )

        messages.success(
            self.request,
            _('%(environment)s environment was successfully created.') % {
                'environment': self.object,
            }
        )

        return response


@method_decorator([
    login_required,
    staff_member_required
], name='dispatch')
class EnvironmentsUpdateView(UpdateView):

    template_name = 'app/environments/update.html'

    fields = ('name', 'alias', 'order')

    success_url = reverse_lazy('environments')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._prev_data = {}

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        self._prev_data = model_to_dict(obj)
        return obj

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['alias'].widget.attrs.update({
            'readonly': True
        })
        return form

    def form_valid(self, form):

        response = super().form_valid(form)

        if form.has_changed():

            log_update_object(
                obj=self.object,
                user=self.request.user,
                prev_data=self._prev_data
            )

            messages.success(
                self.request,
                _('%(environment)s environment was successfully updated.') % {
                    'environment': self.object,
                }
            )

        return response

    def get_queryset(self):
        return Environment.objects.with_user_perms(
            user=self.request.user,
            perms=(
                'change_environment',
            )
        )


@method_decorator([
    login_required,
    staff_member_required
], name='dispatch')
class EnvironmentsDeleteView(DeleteView):

    template_name = 'app/environments/delete.html'

    success_url = reverse_lazy('environments')

    def delete(self, request, *args, **kwargs):

        response = super().delete(request, *args, **kwargs)

        log_delete_object(
            obj=self.object,
            user=self.request.user
        )

        messages.success(
            self.request,
            _('%(environment)s environment was successfully deleted.') % {
                'environment': self.object,
            }
        )

        return response

    def get_queryset(self):
        return Environment.objects.with_user_perms(
            user=self.request.user,
            perms=(
                'delete_environment',
            )
        )
