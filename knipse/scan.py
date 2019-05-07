# -*- coding: utf-8 -*-

from pathlib import Path
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
        descr = descriptor_from_image(base_folder, file_path, img)
        db.store(descr)
        yield file_path, progress


@click.command(name='scan')
@click.pass_context
def cli_scan(ctx):
    '''Walk all folders below `base_folder`
       and store contained images in database
    '''
    db = ctx.obj['database']
    base_folder = ctx.obj['source']
    click.echo('Scanning images in {}...'.format(base_folder))
    for file_path, progress in scan_images(db, base_folder):
        rel_path = file_path.relative_to(base_folder)
        click.echo('\r{:5.1f}% |{:<40s}| {:<20s}'
                   .format(progress * 100,
                           round(progress * 40) * '#',
                           str(rel_path)),
                   nl=False)
    click.echo()
    click.echo('Scan completed')
