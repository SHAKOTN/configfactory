from django import forms
from django.core.exceptions import ValidationError

from configfactory.exceptions import ConfigUpdateError, JSONEncodeError
from configfactory.models import Config, User
from configfactory.services import (
    generate_api_token,
    get_api_token,
    update_config,
)
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


class UserAPIForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('api_token', 'api_user',)
        widgets = {
            'api_token': forms.TextInput(attrs={
                'readonly': True
            }),
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['api_user'].queryset = User.objects.api()
        user = kwargs.get('instance')
        if user:
            api_token = get_api_token(user)
            self.initial['api_token'] = api_token

    def clean(self):
        self._validate_unique = False
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.is_apiuser:
            user.api_token = generate_api_token()
        else:
            user.api_token = None
        if commit:
            user.save()
        return user
