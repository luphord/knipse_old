# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime
from typing import List, Callable, Optional, Iterable, Tuple  # noqa: 401

import click

from .db import KnipseDB
from .walk import walk_images
from .image import descriptor_from_image


def scan_images(db: KnipseDB, base_folder: Path) \
        -> Iterable[Tuple[Path, float]]:
    '''Walk all folders below `base_folder`
       and store contained images in database
    '''
    recgn = db.get_recognizer()
    for file_path, img, progress in walk_images(base_folder, recgn.filter):
        try:
            img.load()
        except (IOError, AttributeError):
            continue  # image type is not supported => we ignore it
        descr = descriptor_from_image(base_folder, file_path, img)
        db.store(descr)
        yield file_path, progress


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
@click.pass_context
def cli_scan(ctx):
    '''Walk all folders below `base_folder`
       and store contained images in database
    '''
    db = ctx.obj['database']
    base_folder = ctx.obj['source']
    click.echo('Scanning images in {}...'.format(base_folder))
    start = datetime.now()
    line_length = 1
    for file_path, progress in scan_images(db, base_folder):
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
