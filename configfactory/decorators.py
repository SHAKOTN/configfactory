from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def staff_member_required(view_func=None, raise_exception=True):
    return _user_flag_required(
        flag='is_staff',
        view_func=view_func,
        raise_exception=raise_exception
    )


def superuser_required(view_func=None, raise_exception=True):
    return _user_flag_required(
        flag='is_superuser',
        view_func=view_func,
        raise_exception=raise_exception
    )


def _user_flag_required(flag, view_func=None, raise_exception=True):

    def check_flag(user):
        if user.is_active and getattr(user, flag, False):
            return True
        if raise_exception:
            raise PermissionDenied
        return False

    actual_decorator = user_passes_test(check_flag)

    if view_func:
        return actual_decorator(view_func)

    return actual_decorator
