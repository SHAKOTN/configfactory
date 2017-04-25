from django import forms
from django.core.exceptions import ValidationError

from configfactory.exceptions import ConfigUpdateError, JSONEncodeError
from configfactory.models import Config, ApiToken
from configfactory.services import update_config, generate_api_token
from configfactory.utils import json_loads


class ConfigForm(forms.Form):

    settings_json = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 32,
        'style': 'width: 100%'
    }))

    def __init__(self, config: Config, **kwargs):
        super().__init__(**kwargs)
        self._config = config

    def clean_settings_json(self):
        settings_json = self.cleaned_data['settings_json']
        try:
            update_config(
                config=self._config,
                settings_json=settings_json,
                commit=False
            )
        except ConfigUpdateError as e:
            raise ValidationError(str(e))
        return settings_json


class JSONSchemaForm(forms.Form):

    schema_json = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 32,
        'style': 'width: 100%'
    }))

    def clean_schema_json(self):
        schema_json = self.cleaned_data['schema_json']
        try:
            json_loads(schema_json)
        except JSONEncodeError as e:
            raise ValidationError(str(e))
        return schema_json


class ApiTokenForm(forms.ModelForm):

    class Meta:
        model = ApiToken
        fields = ('token',)
        widgets = {
            'token': forms.TextInput(attrs={
                'readonly': True
            })
        }

    def save(self, commit=True):
        self.instance.token = generate_api_token()
        return super().save(commit=commit)
