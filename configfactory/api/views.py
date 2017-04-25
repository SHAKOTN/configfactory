from rest_framework.exceptions import ValidationError
from rest_framework.fields import NullBooleanField
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from configfactory.api.serializers import EnvironmentSerializer
from configfactory.models import Environment, User
from configfactory.services import get_settings


class EnvironmentsAPIView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):

        environments = Environment.objects.with_user_perms(
            user=request.user,
            perms=(
                'view_environment',
            ),
        )

        serializer = EnvironmentSerializer(
            environments,
            many=True,
            context={
                'request': request,
                'token': request.auth
            }
        )

        return Response(serializer.data)


class EnvironmentSettingsAPIView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, alias):

        user = request.user  # type: User

        environment = get_object_or_404(
            queryset=Environment.objects.with_user_perms(
                user=user,
                perms=(
                    'view_environment',
                ),
            ).only('pk'),
            alias=alias
        )

        data = get_settings(
            environment=environment,
            user=user,
            flatten=self.get_flatten(request),
            inject=True
        )

        return Response(data)

    def get_flatten(self, request):
        try:
            return (
                NullBooleanField()
                .to_internal_value(request.query_params.get('flatten'))
            )
        except ValidationError:
            return False
