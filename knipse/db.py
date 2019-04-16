# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime
from pathlib import Path

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

_GET_IMAGES = '''SELECT * FROM images;'''

_DT_FMT = '''%Y-%m-%d %H:%M:%S.%f'''


class KnipseDB:

    def __init__(self, connection_string: str):
        self.db = sqlite3.connect(connection_string)
        self._setup_db()

    def _setup_db(self):
        with self.db as conn:
            conn.execute(_CREATE_IMAGE_TABLE)

    def store(self, descriptor: ImageDescriptor):
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
            conn.execute(_INSERT_IMAGE, data)

    def list_images(self):
        with self.db as conn:
            for row in conn.execute(_GET_IMAGES):
                yield ImageDescriptor(
                    Path(row[0]),
                    datetime.strptime(row[1], _DT_FMT),
                    datetime.strptime(row[2], _DT_FMT),
                    row[3],
                    row[4]
                )

    def get_recognizer(self):
        return ImageRecognizer(self.list_images())


class ImageRecognizer:

    def __init__(self, known_images):
        known_images = list(known_images)
        self.known_files = {str(descr.path): descr.modified_at
                            for descr in known_images}
        self.index_md5 = {descr.md5: descr
                          for descr in known_images}

    def filter(self, source, path, mtime):
        rel_path = str(path.relative_to(source))
        return rel_path not in self.known_files \
            or self.known_files[rel_path] != mtime

    def by_md5(self, md5):
        return self.index_md5.get(md5)
