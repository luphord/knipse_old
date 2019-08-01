# -*- coding: utf-8 -*-

from pathlib import Path

import click

from .image import open_image_and_rotate
from .descriptor import ImageDescriptor
from .db import KnipseDB, THUMBNAIL_SIZES


def update_thumbnails(db: KnipseDB, base_folder: Path, descr: ImageDescriptor):
    img_path = base_folder / descr.path
    for size in THUMBNAIL_SIZES:
        thumb = open_image_and_rotate(img_path)
        thumb.thumbnail(size)
        db.store_thumbnail(descr, thumb, size)


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
