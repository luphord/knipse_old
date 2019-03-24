# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime

from PIL import Image

from .descriptor import ImageDescriptor
from .dhash import dhash_bytes


class _EXIF:
    CREATION_DATE = 36867


def _get_creation_time(path: Path, img: Image) -> datetime:
    if hasattr(img, '_getexif'):
        exif = img._getexif()
        if exif and _EXIF.CREATION_DATE in exif:
            return datetime.strptime(exif[_EXIF.CREATION_DATE],
                                     '%Y:%m:%d %H:%M:%S')
    return datetime.fromtimestamp(os.path.getmtime(path))


def descriptor_from_image(source: Path,
                          path: Path,
                          img: Image) -> ImageDescriptor:
    source = Path(source).resolve()
    path = Path(path).resolve()
    creation_date = _get_creation_time(path, img)
    dhsh = dhash_bytes(img)
    return ImageDescriptor(path.relative_to(source), creation_date, dhsh)
