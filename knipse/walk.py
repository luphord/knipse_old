# -*- coding: utf-8 -*-

import os
from pathlib import Path
import click
from PIL import Image


def walk_images(base_folder):
    for dir, subdirs, files in os.walk(str(base_folder)):
        for fname in files:
            try:
                file_path = Path(dir) / fname
                Image.open(file_path)
                yield file_path
            except IOError:
                pass  # not an image


@click.command(name='walk')
@click.argument('base_folder',
                type=click.Path(exists=True, file_okay=False, dir_okay=True,
                                resolve_path=True))
def cli_walk(base_folder):
    '''Recursively list all images below `base_folder`'''
    for x in walk_images(base_folder):
        click.echo(x)
