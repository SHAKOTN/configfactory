import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))

BASE_DIR = os.path.dirname(APP_DIR)

TESTS_DIR = os.path.join(BASE_DIR, 'tests')

DEFAULT_CONFIG = os.path.join(BASE_DIR, 'configfactory.dist.ini')
