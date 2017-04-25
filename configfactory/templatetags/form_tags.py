from django.template import Library

register = Library()


@register.filter
def addclass(field, class_):
    field_class = field.field.widget.attrs.get('class')
    if field_class:
        field_class = ' '.join(set(field_class.split() + class_.split()))
    else:
        field_class = class_
    field.field.widget.attrs['class'] = field_class
    return field
