from django.utils.translation import ugettext_lazy as _
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from configfactory.models import User


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
            user = User.objects.active().get(api_token=token)
        except User.DoesNotExist:
            raise AuthenticationFailed(_('Invalid token.'))

        if not user.has_api_access:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        return user, token
