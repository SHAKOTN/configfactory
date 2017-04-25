import abc
from typing import Tuple

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)
from guardian.shortcuts import get_objects_for_user, get_perms

from configfactory.exceptions import ComponentDeleteError
from configfactory.forms import ConfigForm, JSONSchemaForm
from configfactory.models import Component, Environment, JSONSchema, User, UserComponentStar
from configfactory.services import (
    add_component_star,
    delete_component,
    get_config_settings,
    log_create_object,
    log_delete_object,
    log_update_object,
    remove_component_star,
    update_config,
)
from configfactory.shortcuts import assign_default_perms, get_all_permissions
from configfactory.utils import model_to_dict


@method_decorator(login_required, name='dispatch')
class ComponentListView(ListView):

    template_name = 'app/components/list.html'

    context_object_name = 'components'

    paginate_by = 25

    def get(self, request, *args, **kwargs):
        if not Component.objects.exists():
            return redirect('create_component')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Component.objects.with_user_perms(
            user=self.request.user,
            perms=(
                'view_component',
            ),
        )
        search = self.request.GET.get('search')
        if search:
            return queryset.filter(
                Q(name__icontains=search) |
                Q(alias__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        components = context['object_list']

        components_perms = get_all_permissions(
            user=self.request.user,
            object_list=components
        )

        components_stars = list(
            UserComponentStar.objects.filter(
                user=self.request.user,
                component__in=components
            ).values_list('component_id', flat=True)
        )

        context.update({
            'components_perms': components_perms,
            'components_search': self.request.GET.get('search'),
            'components_stars': components_stars
        })

        return context


class ComponentStarToggleView(View):

    def post(self, request, pk):
        status = None
        toggled = False
        try:
            component = Component.objects.with_user_perms(
                user=request.user,
                perms=(
                    'view_component',
                ),
            ).get(pk=pk)
            status, toggled = self.toggle_star(component)
        except Component.DoesNotExist:
            pass
        return JsonResponse({
            'status': status,
            'toggled': toggled
        })

    @abc.abstractmethod
    def toggle_star(self, component: Component) -> Tuple[bool, bool]:
        pass


@method_decorator([
    login_required,
    csrf_exempt,
], name='dispatch')
class ComponentStarAddView(ComponentStarToggleView):

    def toggle_star(self, component: Component):
        return True, add_component_star(
            user=self.request.user,
            component=component
        )


@method_decorator([
    login_required,
    csrf_exempt
], name='dispatch')
class ComponentStarRemoveView(ComponentStarToggleView):

    def toggle_star(self, component: Component):
        return False, remove_component_star(
            user=self.request.user,
            component=component
        )


@method_decorator(login_required, name='dispatch')
class ComponentCreateView(CreateView):

    template_name = 'app/components/create.html'

    queryset = Component.objects.all()

    fields = ('name', 'alias', 'is_global', 'use_schema')

    def get_success_url(self):
        return reverse('update_component_base_settings', kwargs={
            'pk': self.object.pk
        })

    def form_valid(self, form):

        response = super().form_valid(form)

        user = self.request.user  # type: User

        if not user.is_superuser:
            assign_default_perms(user, self.object)

        log_create_object(
            instance=self.object,
            user=user
        )

        messages.success(
            self.request,
            _('%(component)s component was successfully created.') % {
                'component': self.object,
            }
        )
        return response


@method_decorator(login_required, name='dispatch')
class ComponentUpdateView(UpdateView):

    template_name = 'app/components/update.html'

    fields = ('name', 'alias', 'is_global', 'use_schema')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._prev_data = {}

    def get_queryset(self):
        return get_objects_for_user(
            user=self.request.user,
            perms=(
                'change_component',
            ),
            klass=Component
        )

    def get_object(self, queryset=None):
        object_ = super().get_object(queryset=queryset)
        self._prev_data = model_to_dict(object_)
        return object_

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['alias'].widget.attrs.update({
            'readonly': True
        })
        form.fields['is_global'].widget.attrs.update({
            'disabled': True
        })
        return form

    def form_valid(self, form):

        response = super().form_valid(form)

        log_update_object(
            obj=self.object,
            user=self.request.user,
            prev_data=self._prev_data
        )

        messages.success(
            self.request,
            _('%(component)s component was successfully updated.') % {
                'component': self.object,
            }
        )

        return response

    def get_success_url(self):
        return self.request.GET.get(
            'next',
            reverse('components')
        )


@method_decorator(login_required, name='dispatch')
class ComponentDeleteView(DeleteView):

    template_name = 'app/components/delete.html'

    success_url = reverse_lazy('components')

    context_object_name = 'component'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(
            object=self.object,
            delete_error=kwargs.get('delete_error')
        )
        return self.render_to_response(context)

    def delete(self, request, *args, **kwargs):

        component = self.get_object()
        self.object = component
        success_url = self.get_success_url()

        try:

            delete_component(self.object)

            log_delete_object(
                obj=self.object,
                user=request.user
            )

            messages.success(
                self.request,
                _('%(component)s component was successfully deleted.') % {
                    'component': self.object,
                }
            )

            return redirect(success_url)

        except ComponentDeleteError as e:

            kwargs.update({
                'delete_error': e.message
            })

            return self.get(request, *args, **kwargs)

    def get_queryset(self):
        return get_objects_for_user(
            user=self.request.user,
            perms=(
                'delete_component',
            ),
            klass=Component
        )


@method_decorator(login_required, name='dispatch')
class ComponentSettingsView(TemplateView):

    template_name = 'app/components/settings.html'

    base_settings_viewname = 'component_base_settings'

    env_settings_viewname = 'component_env_settings'

    components_perms = ('view_component',)

    def get(self, request, *args, **kwargs):

        context = self.get_context_data(**kwargs)
        config = context['config']
        view_toggle = request.GET.get('view', 'normal')

        settings_json = get_config_settings(
            config=config,
            flatten=view_toggle == 'flatten',
            secure=True,
            inject=True,
            raw=True
        )

        form = ConfigForm(
            config=config,
            initial={
                'settings_json': settings_json
            }
        )
        form.fields['settings_json'].widget.attrs.update({
            'rows': self.get_rows_length(settings_json)
        })

        context.update({
            'form': form,
            'view_toggle': view_toggle
        })

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):

        user = self.request.user  # type: User

        components = Component.objects.with_user_perms(
            user=user,
            perms=self.components_perms,
        ).prefetch_related('configs')
        component_id = kwargs['pk']
        component = get_object_or_404(
            klass=components,
            pk=component_id
        )

        environment = None

        if 'alias' in kwargs:
            environment = get_object_or_404(
                klass=Environment.objects.with_user_perms(
                    user=user,
                    perms=(
                        'view_environment',
                    )
                ),
                alias=kwargs['alias']
            )

        config = get_object_or_404(
            klass=component.configs.select_related('environment'),
            environment=environment
        )
        config_url = self.get_config_url(**kwargs)

        component_perms = get_perms(user, component)

        kwargs.update({
            'environment': environment,
            'component': component,
            'component_perms': component_perms,
            'config': config,
            'config_url': config_url
        })

        return super().get_context_data(**kwargs)

    def get_config_url(self, **kwargs):
        viewname = self.base_settings_viewname
        viewkwargs = {
            'pk': kwargs['pk']
        }
        if 'alias' in kwargs:
            viewname = self.env_settings_viewname
            viewkwargs.update({
                'alias': kwargs['alias']
            })
        return reverse(viewname, kwargs=viewkwargs)

    def get_rows_length(self, content):
        return min(max(len(content.splitlines()), 24), 32)


@method_decorator(login_required, name='dispatch')
class ComponentSettingsUpdateView(ComponentSettingsView):

    template_name = 'app/components/update_settings.html'

    base_settings_viewname = 'update_component_base_settings'

    env_settings_viewname = 'update_component_env_settings'

    components_perms = ('change_component',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._prev_data = {}

    def get(self, request, *args, **kwargs):

        context = self.get_context_data(**kwargs)
        config = context['config']

        settings_json = get_config_settings(config, raw=True)

        form = ConfigForm(
            config=config,
            initial={
                'settings_json': settings_json
            }
        )
        form.fields['settings_json'].widget.attrs.update({
            'rows': self.get_rows_length(settings_json)
        })

        context.update({
            'form': form,
        })

        return self.render_to_response(context)

    def post(self, request, **kwargs):

        context = self.get_context_data(**kwargs)
        config = context['config']
        environment = context['environment']

        self._prev_data = model_to_dict(config)

        form = ConfigForm(
            config=config,
            data=request.POST,
        )
        form.fields['settings_json'].widget.attrs.update({
            'rows': self.get_rows_length(
                request.POST.get('settings_json', '')
            )
        })

        if form.is_valid():

            config = update_config(
                config=config,
                settings_json=form.cleaned_data['settings_json'],
                commit=True
            )

            log_update_object(
                obj=config,
                user=self.request.user,
                prev_data=self._prev_data
            )

            messages.success(
                request,
                _('%(component)s %(environment)s settings '
                  'were successfully changed.') % {
                    'component': config.component,
                    'environment': environment or _('Base'),
                }
            )

        context.update({
            'form': form
        })

        return self.render_to_response(context)


@method_decorator(login_required, name='dispatch')
class ComponentJSONSchemaView(TemplateView):

    template_name = 'app/components/json_schema.html'

    def get(self, request, *args, **kwargs):

        context = self.get_context_data(**kwargs)
        json_schema = context['json_schema']

        schema_json = json_schema.schema_json

        form = JSONSchemaForm(
            initial={
                'schema_json': schema_json
            }
        )
        form.fields['schema_json'].widget.attrs.update({
            'rows': self.get_rows_length(schema_json)
        })

        context.update({
            'form': form,
        })

        return self.render_to_response(context)

    def post(self, request, **kwargs):

        context = self.get_context_data(**kwargs)

        component = context['component']
        json_schema = context['json_schema']

        schema_json = json_schema.schema_json

        prev_data = model_to_dict(json_schema)

        form = JSONSchemaForm(data=request.POST)
        form.fields['schema_json'].widget.attrs.update({
            'rows': self.get_rows_length(schema_json)
        })

        if form.is_valid():

            json_schema.schema_json = form.cleaned_data['schema_json']
            json_schema.save()

            log_update_object(
                obj=json_schema,
                object_repr=component.name,
                user=self.request.user,
                prev_data=prev_data
            )

            messages.success(
                request,
                _('%(component)s JSON schema '
                  'was successfully changed.') % {
                    'component': component,
                }
            )

        context.update({
            'form': form,
        })

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):

        data = super().get_context_data(**kwargs)

        components = self.get_components().prefetch_related('configs')
        component_id = kwargs['pk']
        component = get_object_or_404(
            klass=components,
            pk=component_id
        )

        json_schema, created = JSONSchema.objects\
            .get_or_create(component=component)

        data.update({
            'component': component,
            'json_schema': json_schema,
        })

        return data

    def get_rows_length(self, content):
        return min(max(len(content.splitlines()), 24), 32)

    def get_components(self):
        return get_objects_for_user(
            user=self.request.user,
            perms=(
                'change_component',
            ),
            klass=Component
        )
