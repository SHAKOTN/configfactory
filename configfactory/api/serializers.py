from django.utils.http import urlencode
from rest_framework import serializers
from rest_framework.reverse import reverse

from configfactory.models import Environment


class EnvironmentSerializer(serializers.ModelSerializer):

    url = serializers.SerializerMethodField()

    class Meta:
        model = Environment
        fields = ('name', 'alias', 'url')

    def get_url(self, instance):
        request = self.context['request']
        token = self.context['token']
        params = urlencode({
            'token': token
        })
        path = reverse('api:settings', kwargs={
            'alias': instance.alias
        })
        return '{uri}?{params}'.format(
            uri=request.build_absolute_uri(path),
            params=params
        )
