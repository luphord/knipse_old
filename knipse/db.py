# -*- coding: utf-8 -*-

import sqlite3

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

_GET_FILTER = '''SELECT path FROM images;'''

_GET_IMAGES = '''SELECT * FROM images;'''

class KnipseDB:

    def __init__(self, connection_string: str):
        self.db = sqlite3.connect(connection_string)
        self._setup_db()

    def _setup_db(self):
        with self.db as conn:
            conn.execute(_CREATE_IMAGE_TABLE)

    def store(self, descriptor: ImageDescriptor):
        with self.db as conn:
            data = (
                str(descriptor.path),
                descriptor.created_at,
                descriptor.modified_at,
                descriptor.md5,
                descriptor.dhash
            )
            conn.execute(_INSERT_IMAGE, data)

    def get_known_images_filter(self):
        with self.db as conn:
            known_files = set(row[0]
                              for row in conn.execute(_GET_FILTER))

        def _filter(source, path):
            return str(path.relative_to(source)) not in known_files

        return _filter

    def list_images(self):
        with self.db as conn:
            for row in conn.execute(_GET_IMAGES):
                yield ImageDescriptor(*row)
