# -*- coding: utf-8 -*-

import unittest
from pathlib import Path
from datetime import datetime
import re

from knipse.db import KnipseDB, ImageRecognizer, _INSERT_IMAGE, _DT_FMT
from knipse.descriptor import ImageDescriptor, ListDescriptor, \
                              ListEntryDescriptor
from knipse.image import descriptor_from_image
from knipse.walk import walk_images
from knipse.scan import scan_images

from .test_walk import EXPECTED_IMAGES


def store_images(db, base_folder: Path) -> None:
    '''Load descriptors for all images in `base_folder`,
       then store them in database.
    '''
    for file_path, img, progress \
            in walk_images(base_folder, skip_thumbnail_folders=True):
        descr = descriptor_from_image(base_folder, file_path, img)
        db.store_image(descr)


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
                b'\x00\x19\xff\xfe\xfc',
                True)
        self.example_list = ListDescriptor(None,
                                           'My Test List',
                                           Path('data/test/1'))

    def test_table_creation(self) -> None:
        '''Check if database tables have been created.'''
        with self.db.db as conn:
            tables = \
                set([row[1]
                     for row in conn.execute('SELECT * from sqlite_master;')
                     if row[0] == 'table'])
        self.assertIn('images', tables)
        self.assertIn('lists', tables)
        self.assertIn('list_entries', tables)

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
        self.db.store_image(self.example_descriptor)
        retrieved_descr = list(self.db.load_all_images())[0]
        retrieved_descr.image_id = None
        self.assertEqual(self.example_descriptor, retrieved_descr)

    def test_retrieving_invalid_row_with_null_date(self) -> None:
        '''Store an invalid image row with a null modification date
           and test that an error is raised on retrieval.
        '''
        data = ('/', None, None, b'0' * 16, b'0' * 16, 1)
        with self.db.db as conn:
            conn.execute(_INSERT_IMAGE, data)
        with self.assertRaises(AssertionError):
            list(self.db.load_all_images())

    def test_invalid_row_conversion(self) -> None:
        '''Test proper errors for invalid database rows.'''
        row_length = re.compile('.*row length.*', re.IGNORECASE)
        with self.assertRaisesRegex(AssertionError, row_length):
            self.db.descriptor_from_row(())
        dt = datetime.strftime(self.example_descriptor.modified_at, _DT_FMT)
        img_id = re.compile('.*image id.*', re.IGNORECASE)
        with self.assertRaisesRegex(AssertionError, img_id):
            row = (None, '/', None, dt, b'0'*16, b'0'*16, 1)  # type: tuple
            self.db.descriptor_from_row(row)
        path = re.compile('.*path.*', re.IGNORECASE)
        with self.assertRaisesRegex(AssertionError, path):
            row = (0, None, None, dt, b'0'*16, b'0'*16, 1)
            self.db.descriptor_from_row(row)
        with self.assertRaisesRegex(AssertionError, path):
            row = (0, 123, None, dt, b'0'*16, b'0'*16, 1)
            self.db.descriptor_from_row(row)
        mod_date = re.compile('.*modification date.*', re.IGNORECASE)
        with self.assertRaisesRegex(AssertionError, mod_date):
            row = (0, '/', None, None, b'0'*16, b'0'*16, 1)
            self.db.descriptor_from_row(row)
        bad_format = re.compile('.*not match format.*', re.IGNORECASE)
        with self.assertRaisesRegex(ValueError, bad_format):
            row = (0, '/', None, 'bad date', b'0'*16, b'0'*16, 1)
            self.db.descriptor_from_row(row)
        with self.assertRaisesRegex(ValueError, bad_format):
            row = (0, '/', 'bad date', dt, b'0'*16, b'0'*16, 1)
            self.db.descriptor_from_row(row)
        md5 = re.compile('.*md5.*', re.IGNORECASE)
        with self.assertRaisesRegex(AssertionError, md5):
            row = (0, '/', None, dt, None, b'0'*16, 1)
            self.db.descriptor_from_row(row)
        with self.assertRaisesRegex(AssertionError, md5):
            row = (0, '/', None, dt, 'bad type', b'0'*16, 1)
            self.db.descriptor_from_row(row)
        with self.assertRaisesRegex(AssertionError, md5):
            row = (0, '/', None, dt, b'bad length', b'0'*16, 1)
            self.db.descriptor_from_row(row)
        dhash = re.compile('.*perceptual hash.*', re.IGNORECASE)
        with self.assertRaisesRegex(AssertionError, dhash):
            row = (0, '/', None, dt, b'0'*16, None, 1)
            self.db.descriptor_from_row(row)
        with self.assertRaisesRegex(AssertionError, dhash):
            row = (0, '/', None, dt, b'0'*16, 'bad type', 1)
            self.db.descriptor_from_row(row)
        with self.assertRaisesRegex(AssertionError, dhash):
            row = (0, '/', None, dt, b'0'*16, b'bad length', 1)
            self.db.descriptor_from_row(row)
        active = re.compile('.*active.*', re.IGNORECASE)
        with self.assertRaisesRegex(AssertionError, active):
            row = (0, '/', None, dt, b'0'*16, b'0'*16, None)
            self.db.descriptor_from_row(row)
        with self.assertRaisesRegex(AssertionError, active):
            row = (0, '/', None, dt, b'0'*16, b'0'*16, 2)
            self.db.descriptor_from_row(row)

    def test_storing_and_updating(self) -> None:
        '''Store image in database, then store again
           and test if it was updated.
        '''
        self.db.store_image(self.example_descriptor)
        retrieved_images = list(self.db.load_all_images())
        self.assertEqual(1, len(retrieved_images))
        retrieved_descr = retrieved_images[0]
        self.db.store_image(retrieved_descr)  # should only update, not insert
        self.assertEqual(1, len(list(self.db.load_all_images())))

    def test_walking_known_images_in_db(self) -> None:
        '''Walk a folder structure, store all images, then
           walk again and test they are all known.'''
        store_images(self.db, self.src)
        filter = self.db.get_recognizer().filter
        for file_path, img, progress \
                in walk_images(self.src, filter, skip_thumbnail_folders=True):
            raise Exception('should not happen')

    def test_recognizing_images_by_various_attributes(self) -> None:
        '''Walk a folder structure, store all images, then walk
           again and test if they are known by various attributes.'''
        store_images(self.db, self.src)
        recognizer = self.db.get_recognizer()
        for file_path, img, progress \
                in walk_images(self.src, None, skip_thumbnail_folders=True):
            descr = descriptor_from_image(self.src, file_path, img)
            if not recognizer.by_md5(descr.md5):
                raise Exception('should not happen')
            if not recognizer.by_path(self.src, file_path):
                raise Exception('should not happen')
            if not recognizer.by_path(self.src, self.src / descr.path):
                raise Exception('should not happen')
            if not recognizer.by_dhash(descr.dhash):
                raise Exception('should not happen')

    def test_scan_and_scan_again(self) -> None:
        '''Scan a folder structure to store images,
           then scan again and test if they are all known.'''
        cnt = 0
        for file_path, progress in scan_images(self.db, self.src,
                                               skip_thumbnail_folders=True):
            cnt += 1
        self.assertEqual(len(EXPECTED_IMAGES), cnt)
        for file_path, progress in scan_images(self.db, self.src,
                                               skip_thumbnail_folders=True):
            raise Exception('should not happen')

    def test_scan_and_scan_subfolder_again(self) -> None:
        '''Scan a folder structure to store images,
           then scan a subfolder of it again and test if
           all contained images are known. This essentially
           simulates moving of the subfolder to the top of
           the source folder structure.'''
        cnt = 0
        for file_path, progress in scan_images(self.db, self.src,
                                               skip_thumbnail_folders=True):
            cnt += 1
        self.assertEqual(len(EXPECTED_IMAGES), cnt)
        for file_path, progress in scan_images(self.db, self.src / 'folder2',
                                               skip_thumbnail_folders=True):
            raise Exception('images in subfolder not recognized')

    def test_removal_of_duplicate_dhashes_in_index(self) -> None:
        '''Create and ImageRecognizer with duplicate dhashes
           and test if they are removed from index.'''
        recgn = ImageRecognizer([self.example_descriptor] * 2)
        # same path -> coerced into one file in path index
        self.assertEqual(1, len(recgn.known_files))
        # same md5 -> coerced into one file in md5 index
        self.assertEqual(1, len(recgn.index_md5))
        # same dhash -> removed from index
        self.assertEqual(0, len(recgn.index_dhash))

    def test_storing_list_descriptors(self) -> None:
        '''Store list in database and check the table count.'''
        images = [self.example_descriptor] * 3
        lst = self.db.store_list(self.example_list, images)
        with self.db.db as conn:
            cnt = conn.execute('SELECT count(*) FROM lists;').fetchone()[0]
            self.assertEqual(1, cnt)
            cnt = conn.execute('SELECT count(*) FROM images;').fetchone()[0]
            self.assertEqual(len(images), cnt)
            cnt = conn.execute('SELECT count(*) FROM list_entries;') \
                      .fetchone()[0]
            self.assertEqual(len(images), cnt)
        entries = list(self.db.load_list_entries(lst))
        self.assertEqual(len(images), len(entries))
        for list_entry, img in entries:
            self.assertEqual(lst.list_id, list_entry.list_id)

    def test_storing_list_entry_descriptors(self) -> None:
        '''Store list entry in database and check the table count.'''
        images = [self.example_descriptor] * 3
        list_descr = self.db.store_list(self.example_list, images)
        assert isinstance(list_descr.list_id, int)
        list_entry_descr = ListEntryDescriptor(None, list_descr.list_id,
                                               1, 10.0)
        list_entry_descr = self.db.store_list_entry(list_entry_descr)
        self.assertEqual(10.0, list_entry_descr.position)
        with self.db.db as conn:
            cnt = conn.execute('SELECT count(*) FROM lists;').fetchone()[0]
            self.assertEqual(1, cnt)
            cnt = conn.execute('SELECT count(*) FROM images;').fetchone()[0]
            self.assertEqual(len(images), cnt)
            cnt = conn.execute('SELECT count(*) FROM list_entries;') \
                      .fetchone()[0]
            self.assertEqual(len(images) + 1, cnt)
            list_entry_descr.position = 11.0
            descr2 = self.db.store_list_entry(list_entry_descr)
            cnt = conn.execute('SELECT count(*) FROM list_entries;') \
                      .fetchone()[0]
            self.assertEqual(len(images) + 1, cnt)  # not increased
            self.assertEqual(11.0, descr2.position)

    def test_loading_all_list_descriptors(self) -> None:
        '''Store list in database and load again.'''
        images = [self.example_descriptor] * 3
        lists = []
        lists.append(self.db.store_list(self.example_list, images))
        lists.append(self.db.store_list(self.example_list, images))
        loaded_lists = list(self.db.load_all_list_descriptors())
        self.assertEqual(lists, loaded_lists)
