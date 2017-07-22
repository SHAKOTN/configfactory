import os

import appdirs

from configfactory import config, paths

SECRET_KEY = 'ky5b5*n(63ko=5#s2hm^#0fc_#f!c)qjes+s716_a_5*vc8((j'

DEBUG = config.getboolean(
    'main',
    'debug',
    fallback=True
)

ALLOWED_HOSTS = []

INTERNAL_IPS = [
    '127.0.0.1',
]

ROOT_URLCONF = 'configfactory.urls'

WSGI_APPLICATION = 'configfactory.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'guardian',
    'rest_framework',
    'debug_toolbar',
    'compressor',

    'configfactory'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(paths.APP_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'configfactory.context_processors.users',
            ],
        },
    },
]

######################################
# Database settings
######################################
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.{}'.format(
            config.get('database', 'engine', fallback='sqlite3')
        ),
        'NAME': config.get('database', 'name', fallback=':memory:'),
        'USER': config.get('database', 'user', fallback=None),
        'PASSWORD': config.get('database', 'password', fallback=None),
        'HOST': config.get('database', 'host', fallback=None),
        'PORT': config.get('database', 'port', fallback=None),
    }
}

######################################
# Auth settings
######################################
AUTH_USER_MODEL = 'configfactory.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend'
)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

ANONYMOUS_USER_NAME = None

LOGIN_URL = 'login'

LOGIN_REDIRECT_URL = 'dashboard'

######################################
# I18n/i10n settings
######################################
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

######################################
# Static and media settings
######################################
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(paths.APP_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(paths.BASE_DIR, 'node_modules'),
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_ENABLED = True

COMPRESS_OFFLINE = True

COMPRESS_OUTPUT_DIR = 'dist'

######################################
# Cache settings
######################################
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': appdirs.user_config_dir('configfactory'),
    }
}

######################################
# Logging settings
######################################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s - %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    }
}

######################################
# ConfigFactory settings
######################################
GLOBAL_SETTINGS_DEFAULTS = {
    'indent': 4,
    'cleansed_hidden': 'api token key secret pass signature',
    'cleansed_substitute': '***************',
    'inject_validation': True,
}

######################################
# Rest API settings
######################################
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'configfactory.api.authentication.TokenAuthentication',
    )
}
