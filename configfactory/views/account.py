from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView
from rest_framework.reverse import reverse

from configfactory.forms import UserAPIForm
from configfactory.models import User
from configfactory.services import get_api_token


@method_decorator(login_required, name='dispatch')
class PersonalInfoView(UpdateView):

    template_name = 'app/account/personal_info.html'

    fields = ('first_name', 'last_name')

    success_url = reverse_lazy('personal_info')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('Your personal information was successfully changed.')
        )
        return response


@method_decorator(login_required, name='dispatch')
class PasswordChangeView(UpdateView):

    template_name = 'app/account/password.html'

    success_url = reverse_lazy('password_change')

    form_class = PasswordChangeForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        form_kwargs = {
            'initial': self.get_initial(),
            'user': self.request.user
        }
        if self.request.method in ('POST', 'PUT'):
            form_kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return form_class(**form_kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('Your password was successfully changed.')
        )
        return response


@method_decorator(login_required, name='dispatch')
class APISettingsView(UpdateView):

    template_name = 'app/account/api_settings.html'

    success_url = reverse_lazy('api_settings')

    form_class = UserAPIForm

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.has_api_access:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object  # type: User
        api_token = get_api_token(user)
        context.update({
            'api_url': '{uri}?{params}'.format(
                uri=reverse('api:environments', request=self.request),
                params=urlencode({
                    'token': api_token
                })
            )
        })
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('API token was successfully changed.')
        )
        return response
