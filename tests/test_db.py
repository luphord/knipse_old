# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

from knipse.db import KnipseDB
from knipse.image import descriptor_from_image
from knipse.walk import walk_images

from .test_walk import EXPECTED_IMAGES


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
        for file_path, img, progress in walk_images(self.src):
            descr = descriptor_from_image(self.src, file_path, img)
            self.db.store(descr)
        with self.db.db as conn:
            cnt = conn.execute('SELECT count(*) FROM images;').fetchone()[0]
            self.assertEqual(len(EXPECTED_IMAGES), cnt)
