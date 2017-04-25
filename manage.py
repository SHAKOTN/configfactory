#!/usr/bin/env python
import os
import sys

from configfactory.paths import DEFAULT_CONFIG

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configfactory.settings')
    os.environ.setdefault('CONFIGFACTORY_CONFIG', DEFAULT_CONFIG)
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
