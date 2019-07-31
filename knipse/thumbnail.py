# -*- coding: utf-8 -*-

import io
from pathlib import Path

import click
from PIL import Image

from .descriptor import ImageDescriptor
from .db import KnipseDB


def update_thumbnails(db: KnipseDB, base_folder: Path, descr: ImageDescriptor):
    img_path = base_folder / descr.path
    img = Image.open(str(img_path))
    thumb = img.resize((300, 200))
    stream = io.BytesIO()
    thumb.save(stream, format='JPEG')
    db.store_thumbnail(descr, stream.getvalue(), 't300x200')


def update_all_thumbnails(db: KnipseDB, base_folder: Path):
    images = list(db.load_all_images())
    for descr in images:
        update_thumbnails(db, base_folder, descr)


@click.command(name='update-thumbnails')
@click.pass_context
def cli_update_thumbnails(ctx):
    '''Update all thumbnails in database.'''
    db = ctx.obj['database']
    base_folder = ctx.obj['source']
    update_all_thumbnails(db, base_folder)
