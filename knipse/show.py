# -*- coding: utf-8 -*-

import click

from .descriptor import ListDescriptor
from .util import FIELDS


@click.command(name='show-list')
@click.option('-f', '--fields', type=FIELDS,
              default='list_id;list_entry_id;image_id;position;path',
              show_default=True,
              help='fields of knipse object to output')
@click.option('-h', '--header/--no-header', default=False,
              show_default=True,
              help='print column headers')
@click.argument('list-id', type=click.STRING, nargs=-1)
@click.pass_context
def cli_show_list(ctx, fields, header, list_id):
    '''Show lists corresponding to `list_id`(s)'''
    db = ctx.obj['database']
    list_ids = [int(obj[1:] if obj.upper().startswith('L') else int(obj))
                for obj in list_id]
    lists = [list(db.load_list_entries(ListDescriptor(list_id, None, '')))
             for list_id in list_ids]
    first_img = lists[0][0] if lists and lists[0] else []
    if header:
        click.echo(fields.headers_tab(*first_img))
    for lst in lists:
        for list_entry, img in lst:
            click.echo(fields.tab(list_entry, img))


@click.command(name='show-image')
@click.option('-f', '--fields', type=FIELDS,
              default='image_id;active;created_at;path',
              show_default=True,
              help='fields of knipse object to output')
@click.option('-h', '--header/--no-header', default=False,
              show_default=True,
              help='print column headers')
@click.argument('image-id', type=click.STRING, nargs=-1)
@click.pass_context
def cli_show_image(ctx, fields, header, image_id):
    '''Show images corresponding to `image_id`(s)'''
    db = ctx.obj['database']
    if not image_id:
        images = list(db.load_all_images())
    else:
        image_ids = [int(obj[1:])
                     if obj.upper().startswith('I')
                     else int(obj)
                     for obj in image_id]
        images = [db.load_image(img_id) for img_id in image_ids]
    if header:
        click.echo(fields.headers_tab(images[0] if images else None))
    for image in images:
        click.echo(fields.tab(image))
