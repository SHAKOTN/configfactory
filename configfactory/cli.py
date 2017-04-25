import functools
import os
import shutil

import click
import django
from dj_static import Cling
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

from configfactory import paths
from configfactory.server import ServerApplication


@click.group()
@click.option(
    '-c',
    '--config',
    required=False,
    envvar='CONFIGFACTORY_CONFIG',
    type=click.Path(exists=True),
)
@click.pass_context
def cli(ctx, config):

    subcommand = ctx.command.commands[ctx.invoked_subcommand]
    context_settings = subcommand.context_settings

    if context_settings.get('obj', {}).get('django_setup'):

        if config is None:
            raise click.MissingParameter(
                param_type='option',
                param_hint='"--config".'
            )

        os.environ['DJANGO_SETTINGS_MODULE'] = 'configfactory.settings'
        os.environ['CONFIGFACTORY_CONFIG'] = config

        django.setup()


command = cli.command
app_command = functools.partial(
    cli.command,
    context_settings={
        'obj': {
            'django_setup': True
        }
    }
)


@command()
@click.argument(
    'f',
    type=click.Path(exists=True)
)
def init(f):
    """Initialize ConfigFactory configuration."""

    dst = os.path.join(
        f, 'configfactory.ini'
    )

    if os.path.exists(dst):
        if not click.confirm(
                '`{}` already exists. '
                'Are you sure you want to override it?'.format(
                    dst
                )
        ):
            return

    shutil.copyfile(
        paths.DEFAULT_CONFIG,
        dst
    )

    click.echo(
        'ConfigFactory settings file saved to: {}'.format(dst)
    )

    click.echo(
        'Please, edit settings file and '
        'run `configfactory migrate` command.'
    )


@app_command()
@click.option(
    '-h',
    '--host',
    help='TCP/IP host to serve on (default: 127.0.0.1).',
    default='127.0.0.1'
)
@click.option(
    '-p',
    '--port',
    help='TCP/IP port to serve on (default: 8080).',
    type=click.INT,
    default='8080'
)
@click.option(
    '-w',
    '--workers',
    help='The number of worker processes for handling requests.',
    type=click.INT,
    default=1
)
def run(host, port, workers):
    """Run ConfigFactory server."""

    from configfactory import settings

    wsgi_app = Cling(get_wsgi_application())

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


@app_command()
def create_superuser():
    """Create super user."""

    call_command('createsuperuser')


@app_command()
def migrate():
    """Migrate ConfigFactory database."""

    call_command('migrate')


def main():
    cli(obj={})


if __name__ == '__main__':
    main()
