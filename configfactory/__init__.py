from django.utils.module_loading import autodiscover_modules

default_app_config = 'configfactory.apps.ConfigFactoryConfig'


def autodiscover():

    # Autodiscover signals subscribers
    autodiscover_modules('subscribers')
