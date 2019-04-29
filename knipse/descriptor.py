# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime
from typing import Optional


class ImageDescriptor:
    '''Container for image metadata like path or modification date.
       In-memory representation of individual rows of the main
       database table.
    '''

    def __init__(self,
                 image_id: Optional[int],
                 path: Path,
                 created_at: Optional[datetime],
                 modified_at: datetime,
                 md5: bytes,
                 dhash: bytes) -> None:
        self.image_id = image_id
        self.path = Path(path)
        self.created_at = created_at
        self.modified_at = modified_at
        self.md5 = md5
        self.dhash = dhash

    def _fields_iter(self):
        yield 'image_id', self.image_id
        yield 'path', self.path
        yield 'created_at', self.created_at
        yield 'modified_at', self.modified_at
        yield 'md5', self.md5
        yield 'dhash', self.dhash

    def __eq__(self, other):
        if not isinstance(other, ImageDescriptor):
            return False
        return all(a == b
                   for a, b in zip(self._fields_iter(), other._fields_iter()))

    def __repr__(self) -> str:
        fields = ', '.join('{}={!r}'.format(key, value)
                           for key, value in self._fields_iter())
        return 'ImageDescriptor({})'.format(fields)

    def __str__(self) -> str:
        return '\t'.join('{}'.format(value.hex()
                                     if isinstance(value, bytes)
                                     else value)
                         for _, value in self._fields_iter())
