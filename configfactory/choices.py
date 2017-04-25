from django.utils.translation import ugettext_lazy as _

from configfactory import constants

ACTIONS = (
    (constants.ACTION_CREATE, _('create')),
    (constants.ACTION_UPDATE, _('update')),
    (constants.ACTION_DELETE, _('delete')),
)
