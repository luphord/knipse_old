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

    def list_images(self) -> Iterable[ImageDescriptor]:
        '''Get images contained in database as `ImageDescriptor` instances.'''
        with self.db as conn:
            for row in conn.execute(_GET_IMAGES):
                created_at = datetime.strptime(row[2], _DT_FMT) \
                    if row[2] else None
                modified_at_str = row[3]
                assert modified_at_str is not None, \
                    'Modification date in row {} may not be None'.format(row)
                modified_at = datetime.strptime(modified_at_str, _DT_FMT)
                yield ImageDescriptor(
                    row[0],
                    Path(row[1]),
                    created_at,
                    modified_at,
                    row[4],
                    row[5]
                )

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

    def by_md5(self, md5: bytes) -> Optional[ImageDescriptor]:
        '''Lookup images by md5 hash.'''
        return self.index_md5.get(md5)
