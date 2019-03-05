# -*- coding: utf-8 -*-

import click
from PIL import Image


def dhash(img: Image) -> int:
    '''Compute the perceptual difference hash (dhash) of the given image
       with row and column differences (128 bit) as described by
       http://www.hackerfactor.com/blog/?/archives/529-Kind-of-Like-That.html
    '''
    thumbnail = img.convert('L').resize((9, 9), Image.BILINEAR)
    pixels = thumbnail.load()
    row_diffs = []
    col_diffs = []
    for row in range(8):
        for col in range(8):
            row_diffs.append(pixels[row + 1, col] >= pixels[row, col])
            col_diffs.append(pixels[row, col + 1] >= pixels[row, col])
    bits = ''.join(['1' if bit else '0' for bit in row_diffs + col_diffs])
    return int(bits, 2)


def dhash_bytes(img: Image) -> bytes:
    '''Compute the perceptual difference hash (dhash) of the given image
       with row and column differences (128 bit) as described by
       http://www.hackerfactor.com/blog/?/archives/529-Kind-of-Like-That.html
    '''
    hash_int = dhash(img)
    return hash_int.to_bytes(16, 'little')


@click.command(name='dhash')
@click.argument('file',
                type=click.Path(exists=True, file_okay=True, dir_okay=False,
                                resolve_path=True))
def cli_dhash(file):
    '''Compute the perceptual difference hash of the given file'''
    img = Image.open(file)
    click.echo('{}\t{}'.format(file, dhash_bytes(img).hex()))
