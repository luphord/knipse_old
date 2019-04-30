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
    for file_path, progress in scan_images(db, base_folder):
        click.echo('{:.1f}%\t{}'.format(progress * 100, file_path))
