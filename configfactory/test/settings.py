import os

from configfactory.paths import TESTS_DIR

os.environ.setdefault('CONFIGFACTORY_CONFIG', os.path.join(
    TESTS_DIR,
    'configfactory.ini'
))

# Import default settings
from configfactory.settings import *

# Add or overwrite settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
