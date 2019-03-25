# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from PIL import Image

from .descriptor import ImageDescriptor
from .dhash import dhash_bytes


class _EXIF:
    CREATION_DATE = 36867


def _get_modification_time(path: Path) -> datetime:
    # getmtime does not support Path in Python 3.5 -> need to convert to str
    return datetime.fromtimestamp(os.path.getmtime(str(path)))


def _get_creation_time(path: Path, img: Image) -> Optional[datetime]:
    if hasattr(img, '_getexif'):
        exif = img._getexif()
        if exif and _EXIF.CREATION_DATE in exif:
            return datetime.strptime(exif[_EXIF.CREATION_DATE],
                                     '%Y:%m:%d %H:%M:%S')
    return None


def descriptor_from_image(source: Path,
                          path: Path,
                          img: Image) -> ImageDescriptor:
    source = Path(source).resolve()
    path = Path(path).resolve()
    created_at = _get_creation_time(path, img)
    modified_at = _get_modification_time(path)
    dhsh = dhash_bytes(img)
    return ImageDescriptor(path.relative_to(source),
                           created_at,
                           modified_at,
                           dhsh)
