# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

from PIL import Image

from knipse.dhash import dhash_bytes


_expected_hash = \
    b'\xf1\xf8\xf8\xf1\xfc\xfc\xf4\xf5\x08\xf1\xec\x00\x19\xff\xfe\xfc'


class TestDifferenceHash(unittest.TestCase):

    def setUp(self):
        img_path = Path(__file__).resolve().parent \
                   / 'images' / 'photo01.jpg'
        self.photo = Image.open(str(img_path))

    def test_dhash_regression(self):
        self.assertEqual(_expected_hash, dhash_bytes(self.photo))
