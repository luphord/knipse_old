# -*- coding: utf-8 -*-

import os

import click

from .walk import walk_images
from .image import descriptor_from_image


@click.command(name='symlink')
@click.argument('base_folder',
                type=click.Path(exists=True, file_okay=False, dir_okay=True,
                                resolve_path=True), required=True)
@click.argument('symlink_folder',
                type=click.Path(exists=True, file_okay=False, dir_okay=True,
                                resolve_path=True), default='.')
def cli_symlink(base_folder, symlink_folder):
    '''Recursively list all images below `base_folder` and
       create symlinks in `symlink_folder`'''
    org_folder = os.getcwd()
    try:
        os.chdir(symlink_folder)
        for file_path, img, progress in walk_images(base_folder):
            descr = descriptor_from_image(base_folder, file_path, img)
            click.echo('{:.1f}%\t{}'.format(progress * 100, descr))
            os.symlink(str(base_folder / descr.path), descr.md5.hex())
    finally:
        os.chdir(org_folder)
