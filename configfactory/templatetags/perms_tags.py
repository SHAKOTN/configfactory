from django.template import Library

register = Library()


@register.assignment_tag()
def object_has_perm(perms, obj, perm):
    if obj.pk in perms:
        return perm in perms[obj.pk]
    return False
