# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime
from pathlib import Path
from collections import Counter
from typing import Optional, Iterable
import typing

from .descriptor import ImageDescriptor, ListDescriptor, \
                        ListEntryDescriptor, BaseDescriptor


_CREATE_IMAGE_TABLE = \
    '''CREATE TABLE IF NOT EXISTS images (
        path text,
        created_at timestamp,
        modified_at timestamp,
        md5 blob,
        dhash blob,
        active bool
    );
    '''

_CREATE_LISTS_TABLE = \
    '''CREATE TABLE IF NOT EXISTS lists (
        name text,
        virtual_folder text
    );
    '''

_CREATE_LIST_ENTRIES_TABLE = \
    '''CREATE TABLE IF NOT EXISTS list_entries (
        list_id int,
        image_id int,
        position real,
        FOREIGN KEY (list_id) REFERENCES lists,
        FOREIGN KEY (image_id) REFERENCES images
    );
    '''

_INSERT_IMAGE = \
    '''INSERT INTO images VALUES (
        ?, ?, ?, ?, ?, ?
    );
    '''

_INSERT_LIST = \
    '''INSERT INTO lists VALUES (
        ?, ?
    );
    '''

_INSERT_LIST_ENTRY = \
    '''INSERT INTO list_entries VALUES (
        ?, ?, ?
    );
    '''

_UPDATE_IMAGE = \
    '''UPDATE images
       SET
         path = ?,
         created_at = ?,
         modified_at = ?,
         md5 = ?,
         dhash = ?,
         active = ?
       WHERE rowid = ?;
    '''

_UPDATE_LIST = \
    '''UPDATE lists
       SET
         name = ?,
         virtual_path = ?
       WHERE rowid = ?;
    '''

_UPDATE_LIST_ENTRY = \
    '''UPDATE list_entries
       SET
         list_id = ?,
         image_id = ?,
         position = ?
       WHERE rowid = ?;
    '''

_GET_IMAGES = \
    '''SELECT
         rowid,
         path,
         created_at,
         modified_at,
         md5,
         dhash,
         active
       FROM images
       WHERE
         active = 1;'''

_GET_IMAGES_IN_LIST = \
    '''SELECT
         images.rowid,
         path,
         created_at,
         modified_at,
         md5,
         dhash,
         active
       FROM images, list_entries
       WHERE
         active = 1
         AND images.rowid = list_entries.image_id
         AND list_entries.list_id = ?;'''

_DT_FMT = '''%Y-%m-%d %H:%M:%S.%f'''


class KnipseDB:
    '''Wrapper for the SQLite database in which knipse stores all data.'''

    def __init__(self, connection_string: str) -> None:
        self.db = sqlite3.connect(connection_string)
        self._setup_db()

    def _setup_db(self):
        with self.db as conn:
            conn.execute(_CREATE_IMAGE_TABLE)
            conn.execute(_CREATE_LISTS_TABLE)
            conn.execute(_CREATE_LIST_ENTRIES_TABLE)

    @typing.overload
    def store(self, descriptor: ImageDescriptor) -> ImageDescriptor: ...

    @typing.overload
    def store(self, descriptor: ListDescriptor,
              content: Iterable[ImageDescriptor]) \
        -> ListDescriptor: ...

    @typing.overload
    def store(self, descriptor: ListEntryDescriptor) \
        -> ListEntryDescriptor: ...

    def store(self, descriptor: BaseDescriptor,
              content: Iterable[ImageDescriptor] = None) \
            -> BaseDescriptor:
        '''Store various `descriptor` types in the database.
           If `descriptor` contains an ID, the corresponding row
           is updated.
        '''
        if isinstance(descriptor, ImageDescriptor):
            assert content is None, \
                'Cannot store an ImageDescriptor with content'
            return self._store_image(descriptor)
        elif isinstance(descriptor, ListDescriptor):
            content = content or []
            return self._store_list(descriptor, content)
        elif isinstance(descriptor, ListEntryDescriptor):
            return self._store_list_entry(descriptor)
        else:
            raise NotImplementedError('Storing {}'.format(type(descriptor)))

    def _store_image(self, descriptor: ImageDescriptor) -> ImageDescriptor:
        '''Store `descriptor` in the database. If `descriptor` contains
           an `image_id`, the corresponding row in the database is updated.
        '''
        created_at = datetime.strftime(descriptor.created_at, _DT_FMT) \
            if descriptor.created_at else None
        modified_at = datetime.strftime(descriptor.modified_at, _DT_FMT) \
            if descriptor.modified_at else None
        with self.db as conn:
            data = (
                str(descriptor.path),
                created_at,
                modified_at,
                descriptor.md5,
                descriptor.dhash,
                int(descriptor.active)
            )
            if descriptor.image_id is None:
                cursor = conn.execute(_INSERT_IMAGE, data)
            else:
                cursor = conn.execute(_UPDATE_IMAGE,
                                      (*data, descriptor.image_id))
            return descriptor.with_id(cursor.lastrowid)

    def _store_list(self, lst: ListDescriptor,
                    images: Iterable[ImageDescriptor]) \
            -> ListDescriptor:
        with self.db as conn:
            data = (lst.name, str(lst.virtual_folder))
            if lst.list_id is None:
                cursor = conn.execute(_INSERT_LIST, data)
            else:
                cursor = conn.execute(_UPDATE_LIST, (*data, lst.list_id))
            list_id = cursor.lastrowid
            for i, img in enumerate(images):
                if img.image_id is None:
                    img = self.store(img)
                conn.execute(_INSERT_LIST_ENTRY,
                             (lst.list_id, img.image_id, float(i)))
            return lst.with_id(list_id)

    def _store_list_entry(self, list_entry: ListEntryDescriptor) \
            -> ListEntryDescriptor:
        with self.db as conn:
            data = (list_entry.list_id, list_entry.image_id,
                    list_entry.position)
            if list_entry.list_entry_id is None:
                cursor = conn.execute(_INSERT_LIST_ENTRY, data)
            else:
                cursor = conn.execute(_UPDATE_LIST_ENTRY,
                                      (*data, list_entry.list_entry_id))
            return list_entry.with_id(cursor.lastrowid)

    def descriptor_from_row(self, row: tuple) -> ImageDescriptor:
        '''Parse, check and convert a database row to an `ImageDescriptor`.'''
        assert len(row) == 7, 'Row length must be 7, got {}'.format(len(row))
        (image_id, path_str, created_at_str,
         modified_at_str, md5, dhash, active_int) = row
        assert isinstance(image_id, int), \
            'Image ID must be of type int, got {} of type {}' \
            .format(image_id, type(image_id))
        assert path_str is not None, \
            'path in row {} may not be None'.format(row)
        assert isinstance(path_str, str), \
            'path must be of type string, got {} of type {}' \
            .format(path_str, type(path_str))
        path = Path(path_str)
        created_at = datetime.strptime(created_at_str, _DT_FMT) \
            if created_at_str else None
        assert modified_at_str is not None, \
            'Modification date in row {} may not be None'.format(row)
        modified_at = datetime.strptime(modified_at_str, _DT_FMT)
        assert md5 is not None, \
            'md5 hash in row {} may not be None'.format(row)
        assert isinstance(md5, bytes), \
            'md5 hash must be of type bytes, got {} of type {}' \
            .format(md5, type(md5))
        assert len(md5) == 16, \
            'md5 hash must be of length 16, got {}'.format(len(md5))
        assert dhash is not None, \
            'perceptual hash in row {} may not be None'.format(row)
        assert isinstance(dhash, bytes), \
            'perceptual hash must be of type bytes, got {} of type {}' \
            .format(dhash, type(dhash))
        assert len(dhash) == 16, \
            'perceptual hash must be of length 16, got {}'.format(len(dhash))
        assert isinstance(active_int, int), \
            'active flag must be of type int, got {} of type {}' \
            .format(active_int, type(active_int))
        assert active_int in (0, 1), \
            'active flag must be of 0 or 1, got {}'.format(active_int)
        active = bool(active_int)
        return ImageDescriptor(
                    image_id,
                    Path(path),
                    created_at,
                    modified_at,
                    md5,
                    dhash,
                    active
                )

    def list_images(self, lst: Optional[ListDescriptor] = None) \
            -> Iterable[ImageDescriptor]:
        '''Get images contained in database as `ImageDescriptor` instances.'''
        with self.db as conn:
            cursor = conn.execute(_GET_IMAGES) if lst is None \
                else conn.execute(_GET_IMAGES_IN_LIST, lst.list_id)
            for row in cursor:
                yield self.descriptor_from_row(row)

    def get_recognizer(self) -> 'ImageRecognizer':
        return ImageRecognizer(self.list_images())


class ImageRecognizer:
    '''State of the database at a the moment of creation,
       contains indexes to recognize images by ther hashes, etc.
    '''

    def __init__(self, known_images: Iterable[ImageDescriptor]) -> None:
        known_images = list(known_images)
        # path (relative to source) are unique,
        # we can rely on the file system for that
        self.known_files = {str(descr.path): descr
                            for descr in known_images}
        # md5 entries may not be unique in the database,
        # but if two images share the same md5 hash they are
        # equal on the byte level and hence it does not matter
        # to which one we refer
        self.index_md5 = {descr.md5: descr
                          for descr in known_images}
        # perceptual image hashes are not unique in the database
        # and cannot be relied on for lookup on collision
        dhashes = (descr.dhash for descr in known_images)
        duplicate_hashes = set(dhash for dhash, n in
                               Counter(dhashes).items()
                               if n > 1)
        self.index_dhash = {descr.dhash: descr
                            for descr in known_images
                            if descr.dhash not in duplicate_hashes}

    def filter(self, source: Path, path: Path, mtime: datetime) -> bool:
        '''Filter images by path and modification date.
           Returns `True` if the image is new or modified,
           `False` if the image is already known.
        '''
        rel_path = str(path.relative_to(source))
        return rel_path not in self.known_files \
            or self.known_files[rel_path].modified_at != mtime

    def by_path(self, source: Path, path: Path) -> Optional[ImageDescriptor]:
        '''Lookup images by path.'''
        rel_path = str(path.relative_to(source))
        return self.known_files.get(rel_path)

    def by_md5(self, md5: bytes) -> Optional[ImageDescriptor]:
        '''Lookup images by md5 hash.'''
        return self.index_md5.get(md5)

    def by_dhash(self, dhash: bytes) -> Optional[ImageDescriptor]:
        '''Lookup images by dhash perceptual image hash.'''
        return self.index_dhash.get(dhash)
