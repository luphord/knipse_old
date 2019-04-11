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
