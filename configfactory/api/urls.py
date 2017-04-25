from django.conf.urls import url

from configfactory.api import views

urlpatterns = [

    url(r'^$',
        view=views.EnvironmentsAPIView.as_view(),
        name='environments'),

    url(r'^(?P<alias>[\w-]+)/$',
        view=views.EnvironmentSettingsAPIView.as_view(),
        name='settings'),
]
