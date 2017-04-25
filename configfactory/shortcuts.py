from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import assign_perm


def assign_default_perms(user, obj):
    model_name = obj._meta.model_name
    default_perms = [
        'view_{model_name}'.format(
            model_name=model_name,
        ),
        'change_{model_name}'.format(
            model_name=model_name
        ),
        'delete_{model_name}'.format(
            model_name=model_name
        ),
    ]
    for perm in default_perms:
        assign_perm(perm, user, obj)


def get_all_permissions(user, object_list):
    checker = ObjectPermissionChecker(user)
    checker.prefetch_perms(object_list)
    return {
        obj.pk: checker.get_perms(obj)
        for obj in object_list
    }
