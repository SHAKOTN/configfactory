from collections import OrderedDict

from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from guardian.shortcuts import get_objects_for_user


class UserQuerySet(models.QuerySet):
    pass


class UserManager(BaseUserManager):

    use_in_migrations = True

    def get_queryset(self):
        return UserQuerySet(
            model=self.model,
            using=self.db
        )

    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class EnvironmentQuerySet(models.QuerySet):

    def with_user_perms(self, user, perms):
        return get_objects_for_user(
            user=user,
            perms=perms,
            klass=self.model
        )


class EnvironmentManager(models.Manager):

    def get_queryset(self):
        return EnvironmentQuerySet(
            model=self.model,
            using=self.db
        )

    def with_user_perms(self, user, perms):
        return self.get_queryset().with_user_perms(
            user=user,
            perms=perms
        )


class ComponentQuerySet(models.QuerySet):

    def global_(self):
        return self.filter(is_global=True)

    def not_global(self):
        return self.filter(is_global=False)

    def with_user_perms(self, user, perms):
        return get_objects_for_user(
            user=user,
            perms=perms,
            klass=self.model
        )


class ComponentManager(models.Manager):

    def get_queryset(self):
        return ComponentQuerySet(
            model=self.model,
            using=self.db
        )

    def global_(self):
        return self.get_queryset().global_()

    def not_global(self):
        return self.get_queryset().not_global()

    def with_user_perms(self, user, perms):
        return self.get_queryset().with_user_perms(
            user=user,
            perms=perms
        )


class ConfigQuerySet(models.QuerySet):

    def base(self):
        return self.filter(environment__isnull=True)

    def global_(self):
        return self.filter(component__is_global=True)

    def settings(self):
        return OrderedDict([
            (config.component.alias, config.settings)
            for config in self.all()
        ])


class ConfigManager(models.Manager):

    def get_queryset(self):
        return ConfigQuerySet(
            model=self.model,
            using=self.db
        )

    def base(self):
        return self.get_queryset().base()

    def global_(self):
        return self.get_queryset().global_()

    def settings(self):
        return self.get_queryset().settings()
