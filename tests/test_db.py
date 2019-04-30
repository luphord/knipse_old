# -*- coding: utf-8 -*-

import unittest
from pathlib import Path
from datetime import datetime
import re

from knipse.db import KnipseDB, _INSERT_IMAGE, _DT_FMT
from knipse.descriptor import ImageDescriptor
from knipse.image import descriptor_from_image
from knipse.walk import walk_images
from knipse.scan import scan_images

from .test_walk import EXPECTED_IMAGES


def store_images(db, base_folder: Path) -> None:
    '''Load descriptors for all images in `base_folder`,
       then store them in database.
    '''
    for file_path, img, progress in walk_images(base_folder):
        descr = descriptor_from_image(base_folder, file_path, img)
        db.store(descr)


class TestKnipseDatabase(unittest.TestCase):

    def setUp(self) -> None:
        self.src = Path(__file__).resolve().parent / 'images' / 'various'
        self.db = KnipseDB(':memory:')
        self.example_descriptor = \
            ImageDescriptor(
                None,
                Path('photo01.jpg'),
                None,
                datetime(2019, 1, 1, 11, 11, 11),
                b'\x1d@@L\x99_n\x88L)\xb1\xe4\xef\xe1\xca\x15',
                b'\xf1\xf8\xf8\xf1\xfc\xfc\xf4\xf5\x08\xf1\xec' +
                b'\x00\x19\xff\xfe\xfc')

    def test_table_creation(self) -> None:
        '''Check if database tables have been created.'''
        with self.db.db as conn:
            tables = \
                set([row[1]
                     for row in conn.execute('SELECT * from sqlite_master;')
                     if row[0] == 'table'])
        self.assertIn('images', tables)

    def test_storing_image_descriptors(self) -> None:
        '''Store images in database and check their count.'''
        store_images(self.db, self.src)
        with self.db.db as conn:
            cnt = conn.execute('SELECT count(*) FROM images;').fetchone()[0]
            self.assertEqual(len(EXPECTED_IMAGES), cnt)

    def test_storing_null_dates(self) -> None:
        '''Store image with creation and modification date
           set to None (should be null in database).
        '''
        self.db.store(self.example_descriptor)
        retrieved_descr = list(self.db.list_images())[0]
        retrieved_descr.image_id = None
        self.assertEqual(self.example_descriptor, retrieved_descr)

    def test_retrieving_invalid_row_with_null_date(self) -> None:
        '''Store an invalid image row with a null modification date
           and test that an error is raised on retrieval.
        '''
        data = ('/', None, None, b'0' * 16, b'0' * 16)
        with self.db.db as conn:
            conn.execute(_INSERT_IMAGE, data)
        with self.assertRaises(AssertionError):
            list(self.db.list_images())

    def test_invalid_row_conversion(self) -> None:
        '''Test proper errors for invalid database rows.'''
        row_length = re.compile('.*row length.*', re.IGNORECASE)
        with self.assertRaisesRegex(AssertionError, row_length):
            self.db.descriptor_from_row(())
        mod_date = re.compile('.*modification date.*', re.IGNORECASE)
        with self.assertRaisesRegex(AssertionError, mod_date):
            self.db.descriptor_from_row((0, '/', None, None, b'0'*16, b'0'*16))
        dt = datetime.strftime(self.example_descriptor.modified_at, _DT_FMT)
        img_id = re.compile('.*image id.*', re.IGNORECASE)
        with self.assertRaisesRegex(AssertionError, img_id):
            row = (None, '/', None, dt, b'0'*16, b'0'*16)  # type: tuple
            self.db.descriptor_from_row(row)
        bad_format = re.compile('.*not match format.*', re.IGNORECASE)
        with self.assertRaisesRegex(ValueError, bad_format):
            row = (0, '/', None, 'bad date', b'0'*16, b'0'*16)
            self.db.descriptor_from_row(row)
        with self.assertRaisesRegex(ValueError, bad_format):
            row = (0, '/', 'bad date', dt, b'0'*16, b'0'*16)
            self.db.descriptor_from_row(row)
        md5 = re.compile('.*md5.*', re.IGNORECASE)
        with self.assertRaisesRegex(AssertionError, md5):
            row = (0, '/', None, dt, None, b'0'*16)
            self.db.descriptor_from_row(row)

    def test_storing_and_updating(self) -> None:
        '''Store image in database, then store again
           and test if it was updated.
        '''
        self.db.store(self.example_descriptor)
        retrieved_images = list(self.db.list_images())
        self.assertEqual(1, len(retrieved_images))
        retrieved_descr = retrieved_images[0]
        self.db.store(retrieved_descr)  # should only update, not insert
        self.assertEqual(1, len(list(self.db.list_images())))

    def test_walking_known_images_in_db(self) -> None:
        '''Walk a folder structure, store all images, then
           walk again and test they are all known.'''
        store_images(self.db, self.src)
        filter = self.db.get_recognizer().filter
        for file_path, img, progress in walk_images(self.src, filter):
            raise Exception('should not happen')

    def test_recognizing_images_by_md5(self) -> None:
        '''Walk a folder structure, store all images, then
           walk again and test if they are known by md5.'''
        store_images(self.db, self.src)
        recognizer = self.db.get_recognizer()
        for file_path, img, progress in walk_images(self.src, None):
            descr = descriptor_from_image(self.src, file_path, img)
            if not recognizer.by_md5(descr.md5):
                raise Exception('should not happen')

    def test_scan_and_scan_again(self) -> None:
        '''Scan a folder sctructure to store images,
           then scan again and test if they are all known.'''
        cnt = 0
        for file_path, progress in scan_images(self.db, self.src):
            cnt += 1
        self.assertEqual(len(EXPECTED_IMAGES), cnt)
        for file_path, progress in scan_images(self.db, self.src):
            raise Exception('should not happen')
