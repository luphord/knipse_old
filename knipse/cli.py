# -*- coding: utf-8 -*-

"""Console script for knipse."""
import sys
import click

from .db import KnipseDB
from .dhash import cli_dhash
from .walk import cli_walk
from .symlink import cli_symlink
from .gui import cli_display


@click.group(name='knipse')
@click.option('-d', '--database',
              type=click.Path(file_okay=True, dir_okay=False,
                              resolve_path=True,),
              default='knipse.sqlite',
              show_default=True,
              help='Knipse database to use')
@click.pass_context
def cli_knipse(ctx, database):
    '''Manage your photo collections and lists.'''
    ctx.ensure_object(dict)
    ctx.obj['database'] = KnipseDB(database)
    return 0


@click.command(name='list')
@click.pass_context
def cli_list(ctx):
    db = ctx.obj['database']
    for descr in db.list_images():
        click.echo(descr)


cli_knipse.add_command(cli_dhash)
cli_knipse.add_command(cli_walk)
cli_knipse.add_command(cli_symlink)
cli_knipse.add_command(cli_display)
cli_knipse.add_command(cli_list)


if __name__ == "__main__":
    sys.exit(cli_knipse())
