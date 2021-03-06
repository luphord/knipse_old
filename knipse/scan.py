# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime
from typing import List, Callable, Optional, Iterable, Tuple  # noqa: 401

import click

from .db import KnipseDB
from .walk import walk_images
from .image import descriptor_from_image
from .descriptor import ImageDescriptor


def scan_images(db: KnipseDB, base_folder: Path,
                skip_thumbnail_folders: bool = True) \
        -> Iterable[Tuple[Path, float]]:
    '''Walk all folders below `base_folder`
       and store contained images in database
    '''
    recgn = db.get_recognizer()
    for file_path, img, progress in walk_images(base_folder,
                                                recgn.filter,
                                                skip_thumbnail_folders):
        # at this point we know that either the file path is not known
        # or the modification date has changed
        # ToDo: check if file is still there
        try:
            img.load()
        except (IOError, AttributeError):
            continue  # image type is not supported => we ignore it
        descr = descriptor_from_image(base_folder, file_path, img)
        # next we check if we can find an indentical file in the md5 index
        looked_up_by_md5 = recgn.by_md5(descr.md5)
        if looked_up_by_md5:  # image was moved
            descr.image_id = looked_up_by_md5.image_id
            db.store_image(descr)
        else:  # new image
            db.store_image(descr)
            yield file_path, progress


def purge_images(db: KnipseDB, base_folder: Path) \
        -> Iterable[ImageDescriptor]:
    '''Check all images in database if they are still present
       and deactivate them otherwise.
    '''
    for descr in db.load_all_images():
        if not (base_folder / descr.path).exists():
            descr.active = False
            db.store_image(descr)
            yield descr


def _format_timedelta(dt):
    total_sec = round(dt.total_seconds())
    days = total_sec // (24 * 60 * 60)
    sec_remaining = total_sec - days * 24 * 60 * 60
    hours = sec_remaining // (60 * 60)
    sec_remaining -= hours * 60 * 60
    minutes = sec_remaining // 60
    seconds = sec_remaining - minutes * 60
    if total_sec < 60:
        return '{}s'.format(seconds)
    elif total_sec < 60 * 60:
        return '{}m {}s'.format(minutes, seconds)
    elif total_sec < 24 * 60 * 60:
        return '{}h {}m {}s'.format(hours, minutes, seconds)
    else:
        return '{}d {}h {}m {}s'.format(days, hours, minutes, seconds)


@click.command(name='scan')
@click.option('-t', '--skip-thumbnails/--no-skip-thumbnails', default=True,
              show_default=True,
              help='Skips all folders containing the word "thumbnail".')
@click.pass_context
def cli_scan(ctx, skip_thumbnails):
    '''Walk all folders below global knipse `source`
       and store contained images in database
    '''
    db = ctx.obj['database']
    base_folder = ctx.obj['source']
    click.echo('Scanning images in {}...'.format(base_folder))
    start = datetime.now()
    line_length = 1
    for file_path, progress in scan_images(db, base_folder, skip_thumbnails):
        rel_path = file_path.relative_to(base_folder)
        remaining = (datetime.now() - start) * (1 - progress)
        click.echo('\r' + ' ' * line_length, nl=False)
        line = '\r{:5.1f}% |{:<40s}| ETA {}  Scanning {}...' \
               .format(progress * 100,
                       round(progress * 40) * '#',
                       _format_timedelta(remaining),
                       str(rel_path))
        if len(line) > 120:
            line = line[:117] + '...'
        line_length = len(line)
        click.echo(line, nl=False)
    click.echo()
    click.echo('Scan completed')


@click.command(name='purge')
@click.pass_context
def cli_purge(ctx):
    '''Deactivate images that do not exist anymore.
    '''
    db = ctx.obj['database']
    base_folder = ctx.obj['source']
    click.echo('Purging images in {}...'.format(base_folder))
    for descr in purge_images(db, base_folder):
        click.echo('Deactivating {}'.format(descr.path))
    click.echo('Purge completed')
