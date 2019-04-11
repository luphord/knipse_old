# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

from knipse.db import KnipseDB
from knipse.image import descriptor_from_image
from knipse.walk import walk_images

from .test_walk import EXPECTED_IMAGES


def store_images(db, base_folder):
    for file_path, img, progress in walk_images(base_folder):
        descr = descriptor_from_image(base_folder, file_path, img)
        db.store(descr)


class TestKnipseDatabase(unittest.TestCase):

    def setUp(self):
        self.src = Path(__file__).resolve().parent / 'images' / 'various'
        self.db = KnipseDB(':memory:')

    def test_table_creation(self):
        with self.db.db as conn:
            tables = \
                set([row[1]
                     for row in conn.execute('SELECT * from sqlite_master;')
                     if row[0] == 'table'])
        self.assertIn('images', tables)

    def test_storing_image_descriptors(self):
        store_images(self.db, self.src)
        with self.db.db as conn:
            cnt = conn.execute('SELECT count(*) FROM images;').fetchone()[0]
            self.assertEqual(len(EXPECTED_IMAGES), cnt)

    def test_walking_known_images_in_db(self):
        '''Walk a folder structure, store all images, then
           walk again and test they are all known'''
        store_images(self.db, self.src)
        filter = self.db.get_known_images_filter()
        for file_path, img, progress in walk_images(self.src, filter):
            raise Exception('should not happen')
