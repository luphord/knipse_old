# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime

from .descriptor import ImageDescriptor
from .dhash import dhash_bytes


class _EXIF:
    CREATION_DATE = 36867


def _get_creation_timestamp(path, img):
    if hasattr(img, '_getexif'):
        exif = img._getexif()
        if exif and _EXIF.CREATION_DATE in exif:
            return exif[_EXIF.CREATION_DATE]
    return os.path.getmtime(path)


def descriptor_from_image(source, path, img):
    source = Path(source).resolve()
    path = Path(path).resolve()
    creation_date = datetime.fromtimestamp(_get_creation_timestamp(path, img))
    dhsh = dhash_bytes(img)
    return ImageDescriptor(path.relative_to(source), creation_date, dhsh)
