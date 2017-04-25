from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView

from configfactory.decorators import staff_member_required
from configfactory.models import GlobalSettings
from configfactory.services import log_update_object
from configfactory.settings import GLOBAL_SETTINGS_DEFAULTS
from configfactory.utils import model_to_dict


@method_decorator([
    login_required,
    staff_member_required
], name='dispatch')
class GlobalSettingsUpdateView(UpdateView):

    template_name = 'app/global_settings/update.html'

    fields = '__all__'

    success_url = reverse_lazy('update_global_settings')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._prev_data = {}

    def get_object(self, queryset=None):
        try:
            global_settings = GlobalSettings.objects.get()
            self._prev_data = model_to_dict(global_settings)
            return global_settings
        except GlobalSettings.DoesNotExist:
            return GlobalSettings.objects\
                .create(**GLOBAL_SETTINGS_DEFAULTS)

    def form_valid(self, form):

        redirect = super().form_valid(form)

        log_update_object(
            obj=self.object,
            user=self.request.user,
            prev_data=self._prev_data
        )

        messages.success(
            self.request,
            _('Global settings were successfully changed.')
        )

        return redirect
