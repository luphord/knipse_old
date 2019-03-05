# -*- coding: utf-8 -*-

import click
from PIL import Image


def dhash(img: Image) -> bytes:
    '''Compute the perceptual difference hash (dhash) of the given image
       with row and column differences (128 bit) as described by
       http://www.hackerfactor.com/blog/?/archives/529-Kind-of-Like-That.html
    '''
    return b'123'


@click.command(name='dhash')
@click.argument('file',
                type=click.Path(exists=True, file_okay=True, dir_okay=False,
                                resolve_path=True))
def cli_dhash(file):
    '''Compute the perceptual difference hash of the given file'''
    img = Image.open(file)
    img.load()
    click.echo('{}\t{}'.format(file, dhash(img).hex()))
