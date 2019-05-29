# -*- coding: utf-8 -*-

"""Console script for knipse."""
import sys
import os
import click
import logging.config

from .db import KnipseDB
from .dhash import cli_dhash
from .scan import cli_scan
from .symlink import cli_symlink
from .gui import cli_display
from .show import cli_show
from .lists import cli_list


_DEFAULT_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG'
        }
    }
}


@click.group(name='knipse')
@click.option('-d', '--database',
              type=click.Path(file_okay=True, dir_okay=False,
                              resolve_path=True),
              default=os.path.join(os.path.expanduser('~'), '.knipse.sqlite'),
              envvar='KNIPSE_DATABASE',
              show_default=True,
              help='Knipse database to use.')
@click.option('-s', '--source',
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              resolve_path=True),
              default=os.path.expanduser('~'),
              envvar='KNIPSE_SOURCE',
              show_default=True,
              help='Base folder of image source.')
@click.option('-v', '--verbose/--no-verbose', default=False,
              help='Show detailed log messages.')
@click.pass_context
def cli_knipse(ctx, database, source, verbose):
    '''Manage your photo collections and lists.'''
    click.echo('Starting knipse with database {} and image source {}'
               .format(database, source))
    ctx.ensure_object(dict)
    ctx.obj['database'] = KnipseDB(database)
    ctx.obj['source'] = source
    if verbose:
        logging.config.dictConfig(_DEFAULT_LOGGING_CONFIG)
    return 0


cli_knipse.add_command(cli_dhash)
cli_knipse.add_command(cli_scan)
cli_knipse.add_command(cli_symlink)
cli_knipse.add_command(cli_display)
cli_knipse.add_command(cli_show)
cli_knipse.add_command(cli_list)


if __name__ == "__main__":
    sys.exit(cli_knipse())
