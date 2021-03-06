# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime
import hashlib
import logging
from typing import Optional, Tuple

from PIL import Image

from .descriptor import ImageDescriptor
from .dhash import dhash_bytes
from .util import get_modification_time


logger = logging.getLogger(__name__)


class _EXIF:
    CREATION_DATE = 36867


def _get_creation_time(path: Path, img: Image) -> Optional[datetime]:
    if hasattr(img, '_getexif'):
        exif = img._getexif()
        if exif and _EXIF.CREATION_DATE in exif:
            creation_date_str = exif[_EXIF.CREATION_DATE]
            try:
                return datetime.strptime(creation_date_str,
                                         '%Y:%m:%d %H:%M:%S')
            except ValueError:
                logger.error('Error parsing creation date "{}" of image {}'
                             .format(creation_date_str, path), exc_info=True)
        return None
    return None


def _md5sum(path: Path) -> bytes:
    md5 = hashlib.md5()
    with open(str(path), 'rb') as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            md5.update(data)
    return md5.digest()


def path_and_modification(source: Path, path: Path) -> Tuple[Path, datetime]:
    '''Returns relative path to `source` and modification time of `path`'''
    source = Path(source).resolve()
    path = Path(path).resolve()
    modified_at = get_modification_time(path)
    return path.relative_to(source), modified_at


def descriptor_from_image(source: Path,
                          path: Path,
                          img: Image) -> ImageDescriptor:
    path = Path(path).resolve()
    rel_path, modified_at = path_and_modification(source, path)
    created_at = _get_creation_time(path, img)
    md5 = _md5sum(path)
    dhsh = dhash_bytes(img)
    return ImageDescriptor(None,
                           rel_path,
                           created_at,
                           modified_at,
                           md5,
                           dhsh,
                           True)


def open_image_and_rotate(path: Path):
    '''Open image and rotate according to exif (if available).'''
    img = Image.open(str(path))
    if hasattr(img, '_getexif'):
        orientation = 0x0112
        exif = img._getexif()
        if exif is not None:
            orientation = exif[orientation]
            rotations = {
                3: Image.ROTATE_180,
                6: Image.ROTATE_270,
                8: Image.ROTATE_90
            }
            if orientation in rotations:
                img = img.transpose(rotations[orientation])
    return img
