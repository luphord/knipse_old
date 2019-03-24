# -*- coding: utf-8 -*-

import unittest
from pathlib import Path
from datetime import datetime

from PIL import Image

from knipse.descriptor import ImageDescriptor
from knipse.image import descriptor_from_image


class TestImageDescriptor(unittest.TestCase):

    def setUp(self):
        self.src = Path(__file__).resolve().parent / 'images'
        self.path = self.src / 'forest' / 'forest_snow.jpg'

    def test_descriptor_regression(self):
        '''Regression test for ImageDescriptor of a particular image'''
        expected = ImageDescriptor(
                    Path('forest/forest_snow.jpg'),
                    datetime(2010, 1, 7, 14, 47, 51),
                    datetime(2019, 3, 24, 13, 20, 50, 302073),
                    b'\xef\xe7\x8e\x7f>???\x07\x03\x00\xffs\xff\xff\xe0')
        actual = descriptor_from_image(self.src, self.path,
                                       Image.open(self.path))
        self.assertEqual(expected.path, actual.path)
        self.assertEqual(expected.created_at, actual.created_at)
        # do not compare modification times of images in version control
        # as these depend on the time of checkout
        self.assertEqual(expected.dhash, actual.dhash)
