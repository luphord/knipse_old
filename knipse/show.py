# -*- coding: utf-8 -*-

import click

from .util import FIELDS


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
    '''Show images corresponding to `image_id`(s).'''
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
