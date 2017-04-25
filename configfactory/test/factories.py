import factory.django
from faker import Faker

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):

    email = fake.email()

    class Meta:
        model = 'configfactory.User'
        django_get_or_create = ('email',)


class EnvironmentFactory(factory.django.DjangoModelFactory):

    name = 'Development'

    alias = 'development'

    class Meta:
        model = 'configfactory.Environment'
        django_get_or_create = ('alias',)


class ComponentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'configfactory.Component'
        django_get_or_create = ('alias',)


class ComponentSettingsFactory(factory.django.DjangoModelFactory):

    data = {}

    class Meta:
        model = 'configfactory.Config'
        django_get_or_create = ('environment', 'component')
