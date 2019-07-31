# -*- coding: utf-8 -*-

import io

import click
from PIL import Image


@click.command(name='update-thumbnails')
@click.pass_context
def cli_update_thumbnails(ctx):
    '''Update all thumbnails in database.'''
    db = ctx.obj['database']
    base_folder = ctx.obj['source']
    images = list(db.load_all_images())
    for descr in images:
        img_path = base_folder / descr.path
        img = Image.open(str(img_path))
        thumb = img.resize((300, 200))
        stream = io.BytesIO()
        thumb.save(stream, format='JPEG')
        db.store_thumbnail(descr, stream.getvalue(), 't300x200')
