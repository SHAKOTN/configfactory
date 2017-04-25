from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from configfactory.models import ApiToken


class TokenAuthentication(BaseAuthentication):

    keyword = 'Token'

    def authenticate(self, request):

        if 'token' in request.data:
            token = request.data['token']
        elif 'token' in request.query_params:
            token = request.query_params['token']
        else:
            raise AuthenticationFailed(_('Token is required.'))

        try:
            api_token = ApiToken.objects.select_related('user').get(token=token)
        except ApiToken.DoesNotExist:
            raise AuthenticationFailed(_('Invalid token.'))

        user = api_token.user

        if not user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        return user, token
