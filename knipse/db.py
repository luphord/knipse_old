# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Iterable

from .descriptor import ImageDescriptor


_CREATE_IMAGE_TABLE = \
    '''CREATE TABLE IF NOT EXISTS images (
        path text,
        created_at timestamp,
        modified_at timestamp,
        md5 blob,
        dhash blob
    );
    '''

_INSERT_IMAGE = \
    '''INSERT INTO images VALUES (
        ?, ?, ?, ?, ?
    );
    '''

_UPDATE_IMAGE = \
    '''UPDATE images
       SET
         path = ?,
         created_at = ?,
         modified_at = ?,
         md5 = ?,
         dhash = ?
       WHERE rowid=?;
    '''

_GET_IMAGES = '''SELECT rowid, * FROM images;'''

_DT_FMT = '''%Y-%m-%d %H:%M:%S.%f'''


class KnipseDB:
    '''Wrapper for the SQLite database in which knipse stores all data.'''

    def __init__(self, connection_string: str) -> None:
        self.db = sqlite3.connect(connection_string)
        self._setup_db()

    def _setup_db(self):
        with self.db as conn:
            conn.execute(_CREATE_IMAGE_TABLE)

    def store(self, descriptor: ImageDescriptor) -> None:
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
                descriptor.dhash
            )
            if descriptor.image_id is None:
                conn.execute(_INSERT_IMAGE, data)
            else:
                conn.execute(_UPDATE_IMAGE, (*data, descriptor.image_id))

    def descriptor_from_row(self, row: tuple) -> ImageDescriptor:
        '''Parse, check and convert a database row to an `ImageDescriptor`.'''
        assert len(row) == 6, 'Row length must be 6, got {}'.format(len(row))
        image_id, path_str, created_at_str, modified_at_str, md5, dhash = row
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
        return ImageDescriptor(
                    image_id,
                    Path(path),
                    created_at,
                    modified_at,
                    md5,
                    dhash
                )

    def list_images(self) -> Iterable[ImageDescriptor]:
        '''Get images contained in database as `ImageDescriptor` instances.'''
        with self.db as conn:
            for row in conn.execute(_GET_IMAGES):
                yield self.descriptor_from_row(row)

    def get_recognizer(self) -> 'ImageRecognizer':
        return ImageRecognizer(self.list_images())


class ImageRecognizer:
    '''State of the database at a the moment of creation,
       contains indexes to recognize images by ther hashes, etc.
    '''

    def __init__(self, known_images: Iterable[ImageDescriptor]) -> None:
        known_images = list(known_images)
        self.known_files = {str(descr.path): descr.modified_at
                            for descr in known_images}
        self.index_md5 = {descr.md5: descr
                          for descr in known_images}

    def filter(self, source, path, mtime):
        '''Filter images by path and modification date.
           Returns `True` if the image is new or modified,
           `False` if the image is already known.
        '''
        rel_path = str(path.relative_to(source))
        return rel_path not in self.known_files \
            or self.known_files[rel_path] != mtime

    def by_path(self, source: Path, path: Path):
        '''Lookup images by path.'''
        rel_path = str(path.relative_to(source))
        return self.known_files.get(rel_path)

    def by_md5(self, md5: bytes) -> Optional[ImageDescriptor]:
        '''Lookup images by md5 hash.'''
        return self.index_md5.get(md5)
