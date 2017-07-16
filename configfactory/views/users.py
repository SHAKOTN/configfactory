from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from django_filters.views import FilterView
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import assign_perm, get_objects_for_user, remove_perm

from configfactory.decorators import staff_member_required, superuser_required
from configfactory.filters import UserFilterSet
from configfactory.forms import UserAPIForm
from configfactory.models import Environment, User
from configfactory.services import (
    log_create_object,
    log_delete_object,
    log_update_object,
)
from configfactory.utils import model_to_dict


@method_decorator([
    login_required,
    staff_member_required
], name='dispatch')
class UsersListView(FilterView):

    template_name = 'app/users/list.html'

    paginate_by = 25

    filterset_class = UserFilterSet

    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.exclude(
            pk=self.request.user.pk
        ).order_by('email')


@method_decorator([
    login_required,
    superuser_required
], name='dispatch')
class UsersCreateView(CreateView):

    template_name = 'app/users/create.html'

    queryset = User.objects.all()

    fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'is_superuser',
        'is_apiuser',
    )

    context_object_name = 'user'

    success_url = reverse_lazy('users')

    def form_valid(self, form):

        response = super().form_valid(form)

        log_create_object(
            instance=self.object,
            user=self.request.user,
            fields=self.fields
        )

        messages.success(
            self.request,
            _('%(name)s user was successfully created.') % {
                'name': self.object,
            }
        )

        return response


@method_decorator([
    login_required,
    superuser_required
], name='dispatch')
class UsersUpdateView(UpdateView):

    template_name = 'app/users/update.html'

    queryset = User.objects.all()

    fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'is_superuser',
        'is_apiuser',
    )

    context_object_name = 'user'

    success_url = '.'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._prev_data = {}

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        self._prev_data = model_to_dict(obj, fields=self.fields)
        return obj

    def form_valid(self, form):

        response = super().form_valid(form)

        if form.has_changed():

            log_update_object(
                obj=self.object,
                user=self.request.user,
                prev_data=self._prev_data,
                fields=self.fields
            )

            messages.success(
                self.request,
                _('%(name)s profile was successfully updated.') % {
                    'name': self.object,
                }
            )

        return response


@method_decorator([
    login_required,
    superuser_required
], name='dispatch')
class UsersChangePassword(UpdateView):

    template_name = 'app/users/change_password.html'

    queryset = User.objects.all()

    context_object_name = 'user'

    form_class = SetPasswordForm

    success_url = '.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.object
        })
        if 'instance' in kwargs:
            del kwargs['instance']
        return kwargs

    def form_valid(self, form):

        response = super().form_valid(form)

        if form.has_changed():

            messages.success(
                self.request,
                _('%(name)s user password was successfully updated.') % {
                    'name': self.object,
                }
            )

        return response


@method_decorator([
    login_required,
    superuser_required
], name='dispatch')
class UsersDeleteView(DeleteView):

    template_name = 'app/users/delete.html'

    queryset = User.objects.all()

    context_object_name = 'user'

    success_url = reverse_lazy('users')

    def delete(self, request, *args, **kwargs):

        response = super().delete(request, *args, **kwargs)

        log_delete_object(
            obj=self.object,
            user=self.request.user
        )

        messages.success(
            self.request,
            _('%(name)s was successfully deleted.') % {
                'name': self.object,
            }
        )

        return response


@method_decorator([
    login_required,
    superuser_required
], name='dispatch')
class UsersUpdatePermissionsView(DetailView):

    template_name = 'app/users/update_permissions.html'

    context_object_name = 'user'

    success_url = '.'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._object_cache = {}

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        user = kwargs['object']

        model_name = self.kwargs.get(
            'model',
            Environment._meta.model_name
        )

        try:
            model = apps.get_model(
                app_label='configfactory',
                model_name=model_name
            )
        except LookupError:
            raise Http404

        object_list = get_objects_for_user(
            user=self.request.user,
            perms=(
                'view_{model_name}'.format(
                    model_name=model_name
                ),
            ),
            klass=model
        )

        self._object_cache = {
            obj.pk: obj for obj in object_list
        }

        perms = self.get_user_perms(
            user=user,
            object_list=object_list
        )

        self_perms = self.get_user_perms(
            user=self.request.user,
            object_list=object_list
        )

        context.update({
            'object_list': object_list,
            'model_name': model_name,
            'model': model,
            'perms': perms,
            'self_perms': self_perms
        })

        return context

    def post(self, request, *args, **kwargs):

        self.object = self.get_object()

        context = self.get_context_data(object=self.object)
        perms = context['perms']  # type: list

        form_perms = request.POST.getlist('perms', default=[])
        user_perms = []

        for perm in form_perms:
            user_perms.append(perm)
            for replace in ['change', 'delete']:
                if perm.startswith(replace):
                    view_perm = perm.replace(replace, 'view')
                    if view_perm not in form_perms \
                            and view_perm not in user_perms:
                        user_perms.append(view_perm)

        changed = False

        # Assign new permissions
        for perm in user_perms:
            if perm not in perms:
                perm, obj = self.get_perm_obj(perm)
                assign_perm(
                    perm=perm,
                    user_or_group=self.object,
                    obj=obj
                )
                changed = True

        # Remove permissions
        for perm in perms:
            if perm not in user_perms:
                perm, obj = self.get_perm_obj(perm)
                remove_perm(
                    perm=perm,
                    user_or_group=self.object,
                    obj=obj
                )
                changed = True

        context.update({
            'perms': user_perms
        })

        if changed:
            messages.success(
                self.request,
                _('%(name)s permissions was successfully changed.') % {
                    'name': self.object,
                }
            )

        return self.render_to_response(context)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff and not user.is_superuser:
            return User.objects.exclude(is_superuser=True)
        return User.objects.all()

    def get_user_perms(self, user, object_list):

        checker = ObjectPermissionChecker(user)
        checker.prefetch_perms(object_list)

        perms = []

        for obj in object_list:
            perms.extend([
                ':'.join([
                    perm,
                    str(obj.pk)
                ])
                for perm in checker.get_perms(obj)
            ])

        return perms

    def get_perm_obj(self, perm):
        perm, object_id = perm.split(':')
        object_id = int(object_id)
        obj = self._object_cache[object_id]
        return perm, obj


@method_decorator([
    login_required,
    superuser_required
], name='dispatch')
class UsersUpdateAPISettingsView(UpdateView):

    template_name = 'app/users/update_api_settings.html'

    form_class = UserAPIForm

    context_object_name = 'user'

    success_url = '.'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff and not user.is_superuser:
            return User.objects.exclude(is_superuser=True)
        return User.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object  # type: User
        context['has_users'] = user.is_apiuser and user.users.exists()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.has_changed():
            messages.success(
                self.request,
                _('%(name)s user API settings was successfully updated.') % {
                    'name': self.object,
                }
            )
        return response
