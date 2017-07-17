import os
import shutil

import appdirs
import click
import django
from dj_static import Cling
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

from configfactory import paths
from configfactory.server import ServerApplication


@click.group()
@click.option(
    '--config', '-c',
    required=False,
    envvar='CONFIGFACTORY_CONFIG',
    type=click.Path(),
    default=appdirs.user_config_dir('configfactory.ini')
)
def cli(config):

    if not os.path.exists(config):

        if not click.confirm(
            '`{}` configuration file does not exist. '
            'Do want to create it with default settings ?'.format(config)
        ):
            return

        shutil.copyfile(paths.DEFAULT_CONFIG, config)

        click.echo(
            'ConfigFactory settings file saved to: {}'.format(config)
        )

        click.echo(
            'Please, edit settings file and '
            'run `configfactory migrate` command.'
        )

    os.environ['CONFIGFACTORY_CONFIG'] = config
    os.environ['DJANGO_SETTINGS_MODULE'] = 'configfactory.settings'

    # Setup Django
    django.setup()


@cli.command()
@click.option(
    '--host', '-h',
    help='TCP/IP host to serve on (default: 127.0.0.1).',
    default='127.0.0.1'
)
@click.option(
    '--port', '-p',
    help='TCP/IP port to serve on (default: 8080).',
    type=click.INT,
    default='8080'
)
@click.option(
    '--workers', '-w',
    help='The number of worker processes for handling requests.',
    type=click.INT,
    default=1
)
def run(host, port, workers):
    """Run ConfigFactory server."""

    from configfactory import settings

    wsgi_app = Cling(get_wsgi_application())

    if isinstance(settings.ALLOWED_HOSTS, list):
        settings.ALLOWED_HOSTS.append(host)

    server = ServerApplication(
        wsgi_app=wsgi_app,
        options={
            'bind': '{host}:{port}'.format(
                host=host,
                port=port
            ),
            'workers': workers
        }
    )
    server.run()


@cli.command()
def create_superuser():
    """
    Create super user.
    """
    call_command('createsuperuser')


@cli.command()
def migrate():
    """
    Migrate ConfigFactory database.
    """
    call_command('migrate')


def main():
    cli(obj={})


if __name__ == '__main__':
    main()
