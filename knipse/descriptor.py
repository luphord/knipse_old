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
                 dhash: bytes,
                 active: bool) -> None:
        self.image_id = image_id
        self.path = Path(path)
        self.created_at = created_at
        self.modified_at = modified_at
        self.md5 = md5
        self.dhash = dhash
        self.active = active

    def with_id(self, image_id: int) -> 'ImageDescriptor':
        '''Create a copy of this descriptor with the given `image_id`.'''
        return ImageDescriptor(image_id,
                               self.path,
                               self.created_at,
                               self.modified_at,
                               self.md5,
                               self.dhash,
                               self.active)

    def _fields_iter(self):
        yield 'image_id', self.image_id
        yield 'path', self.path
        yield 'created_at', self.created_at
        yield 'modified_at', self.modified_at
        yield 'md5', self.md5
        yield 'dhash', self.dhash
        yield 'active', self.active

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


class ListDescriptor:
    '''Container for list metadata like name and virtual folder.
       In-memory representation of individual rows of the list
       database table.
    '''

    def __init__(self,
                 list_id: Optional[int],
                 name: str,
                 virtual_folder: Path) -> None:
        self.list_id = list_id
        self.name = name
        self.virtual_folder = Path(virtual_folder)

    def with_id(self, list_id: int) -> 'ListDescriptor':
        '''Create a copy of this descriptor with the given `list_id`.'''
        return ListDescriptor(list_id,
                              self.name,
                              self.virtual_folder)

    def _fields_iter(self):
        yield 'list_id', self.list_id
        yield 'name', self.name
        yield 'virtual_folder', self.virtual_folder

    def __eq__(self, other):
        if not isinstance(other, ListDescriptor):
            return False
        return all(a == b
                   for a, b in zip(self._fields_iter(), other._fields_iter()))

    def __repr__(self) -> str:
        fields = ', '.join('{}={!r}'.format(key, value)
                           for key, value in self._fields_iter())
        return 'List({})'.format(fields)

    def __str__(self) -> str:
        return '\t'.join('{}'.format(value.hex()
                                     if isinstance(value, bytes)
                                     else value)
                         for _, value in self._fields_iter())
