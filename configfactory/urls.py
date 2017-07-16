from django.conf import settings
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from configfactory import views

urlpatterns = [

    url(r'^$',
        view=views.default.dashboard,
        name='dashboard'),

    url(r'^login/$',
        view=auth_views.login,
        name='login',
        kwargs={
            'template_name': 'app/login.html'
        }),

    url(r'^logout/$',
        view=auth_views.logout,
        name='logout',
        kwargs={
            'next_page': 'login'
        }),

    url(r'^personal_info/$',
        view=views.account.PersonalInfoView.as_view(),
        name='personal_info'),

    url(r'^password_change/$',
        view=views.account.PasswordChangeView.as_view(),
        name='password_change'),

    url(r'^api_settings/$',
        view=views.account.APISettingsView.as_view(),
        name='api_settings'),

    url(r'^components/$',
        view=views.components.ComponentListView.as_view(),
        name='components'),

    url(r'^components/create/$',
        view=views.components.ComponentCreateView.as_view(),
        name='create_component'),

    url(r'^components/(?P<pk>[0-9]+)/json_schema/$',
        view=views.components.ComponentJSONSchemaView.as_view(),
        name='component_json_schema'),

    url(r'^components/(?P<pk>[0-9]+)/settings/$',
        view=views.components.ComponentSettingsView.as_view(),
        name='component_base_settings'),

    url(r'^components/(?P<pk>[0-9]+)/settings/update/$',
        view=views.components.ComponentSettingsUpdateView.as_view(),
        name='update_component_base_settings'),

    url(r'^components/(?P<pk>[0-9]+)/settings/(?P<alias>[-\w]+)/$',
        view=views.components.ComponentSettingsView.as_view(),
        name='component_env_settings'),

    url(r'^components/(?P<pk>[0-9]+)/settings/(?P<alias>[-\w]+)/update/$',
        view=views.components.ComponentSettingsUpdateView.as_view(),
        name='update_component_env_settings'),

    url(r'^components/(?P<pk>[0-9]+)/update/$',
        view=views.components.ComponentUpdateView.as_view(),
        name='update_component'),

    url(r'^components/(?P<pk>[0-9]+)/delete/$',
        view=views.components.ComponentDeleteView.as_view(),
        name='delete_component'),

    url(r'^components/(?P<pk>[0-9]+)/add_star/$',
        view=views.components.ComponentStarAddView.as_view(),
        name='add_component_start'),

    url(r'^components/(?P<pk>[0-9]+)/remove_star/$',
        view=views.components.ComponentStarRemoveView.as_view(),
        name='remove_component_start'),

    url(r'^environments/$',
        view=views.environments.EnvironmentsListView.as_view(),
        name='environments'),

    url(r'^environments/create/$',
        view=views.environments.EnvironmentsCreateView.as_view(),
        name='create_environment'),

    url(r'^environments/(?P<pk>[0-9]+)/update/$',
        view=views.environments.EnvironmentsUpdateView.as_view(),
        name='update_environment'),

    url(r'^environments/(?P<pk>[0-9]+)/delete/$',
        view=views.environments.EnvironmentsDeleteView.as_view(),
        name='delete_environment'),

    url(r'^global_settings/$',
        view=views.global_settings.GlobalSettingsUpdateView.as_view(),
        name='update_global_settings'),

    url(r'^logs/$',
        view=views.logs.LogsListView.as_view(),
        name='logs'),

    url(r'^logs/(?P<pk>[0-9]+)/$',
        view=views.logs.LogsDetailView.as_view(),
        name='log_detail'),

    url(r'^users/$',
        view=views.users.UsersListView.as_view(),
        name='users'),

    url(r'^users/create/$',
        view=views.users.UsersCreateView.as_view(),
        name='create_user'),

    url(r'^users/(?P<pk>[0-9]+)/change_password/$',
        view=views.users.UsersChangePassword.as_view(),
        name='change_user_password'),

    url(r'^users/(?P<pk>[0-9]+)/update/$',
        view=views.users.UsersUpdateView.as_view(),
        name='update_user'),

    url(r'^users/(?P<pk>[0-9]+)/update_permissions/$',
        view=views.users.UsersUpdatePermissionsView.as_view(),
        name='update_user_permissions'),

    url(r'^users/(?P<pk>[0-9]+)/update_permissions/(?P<model>\w+)/$',
        view=views.users.UsersUpdatePermissionsView.as_view(),
        name='update_user_permissions_by_model'),

    url(r'^users/(?P<pk>[0-9]+)/update_api_settings/$',
        view=views.users.UsersUpdateAPISettingsView.as_view(),
        name='update_user_api_settings'),

    url(r'^users/(?P<pk>[0-9]+)/delete/$',
        view=views.users.UsersDeleteView.as_view(),
        name='delete_user'),

    url(r'^api/',
        view=include('configfactory.api.urls', namespace='api'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
