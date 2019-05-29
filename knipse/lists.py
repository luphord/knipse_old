# -*- coding: utf-8 -*-

import click

from .descriptor import ListDescriptor


@click.group(name='list')
@click.pass_context
def cli_list(ctx):
    '''Manage lists.'''
    return 0


@click.command(name='create')
@click.argument('name', type=click.STRING, nargs=1)
@click.option('-v', '--virtual-folder',
              type=click.Path(),
              default='',
              required=False,
              show_default=True,
              help='Virtual folder containing the new list.')
@click.pass_context
def cli_create_list(ctx, name, virtual_folder):
    '''Create a new list'''
    db = ctx.obj['database']
    lst = db.store(ListDescriptor(None, name, str(virtual_folder)))
    click.echo('Created list {!r}'.format(lst))


cli_list.add_command(cli_create_list)
