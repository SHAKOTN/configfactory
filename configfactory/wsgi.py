import os

from django.core.wsgi import get_wsgi_application

from configfactory.paths import DEFAULT_CONFIG

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configfactory.settings')
os.environ.setdefault('CONFIGFACTORY_CONFIG', DEFAULT_CONFIG)

application = get_wsgi_application()
