# -*- coding: utf-8 -*-

from pathlib import Path

import click

from .descriptor import ListDescriptor, ListEntryDescriptor
from .db import ImageRecognizer


def image_id_from_string(image_str: str,
                         base_folder: Path,
                         recgn: ImageRecognizer) -> int:
    if image_str.upper().startswith('I'):
        try:
            return int(image_str[1:])
        except ValueError:
            pass  # we received a path instead of an id and handle it below
    image_descr = recgn.by_path(base_folder, Path(image_str).resolve())
    if not image_descr or image_descr.image_id is None:
        raise Exception('{} not found in database'.format(image_str))
    return image_descr.image_id


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
    '''Create a new list.'''
    db = ctx.obj['database']
    lst = db.store(ListDescriptor(None, name, str(virtual_folder)))
    click.echo('Created list {!r}'.format(lst))


@click.command(name='append')
@click.argument('images', type=click.STRING, nargs=-1)
@click.option('-l', '--list-id',
              type=click.STRING,
              required=True,
              help='List to append image(s) to.')
@click.pass_context
def cli_append_to_list(ctx, images, list_id):
    '''Append image(s) to list.'''
    db = ctx.obj['database']
    base_folder = ctx.obj['source']
    recgn = db.get_recognizer()
    lid = int(list_id[1:]) if list_id.upper().startswith('L') else int(list_id)
    lst = ListDescriptor(lid, '', '')
    entries = list(db.load_list_entries(lst))
    current_last_position = entries[-1][0].position if entries else 0
    for i, image in enumerate(images):
        image_id = image_id_from_string(image, base_folder, recgn)
        entry_descr = ListEntryDescriptor(None, lid, image_id,
                                          current_last_position + i + 1)
        db.store(entry_descr)


cli_list.add_command(cli_create_list)
cli_list.add_command(cli_append_to_list)
