# -*- coding: utf-8 -*-

from pathlib import Path

from .descriptor import ImageDescriptor
from .dhash import dhash_bytes


def descriptor_from_image(source, path, img):
    source = Path(source).resolve()
    path = Path(path).resolve()
    dhsh = dhash_bytes(img)
    return ImageDescriptor(path.relative_to(source), dhsh)
