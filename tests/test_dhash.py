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

    def test_dhash_after_resize(self):
        dhsh = dhash_bytes(self.photo)
        photo = self.photo.resize((200, 100), Image.BILINEAR)
        self.assertEqual(dhsh, dhash_bytes(photo))
        photo = self.photo.resize((80, 100), Image.BILINEAR)
        self.assertEqual(dhsh, dhash_bytes(photo))
        photo = self.photo.resize((3000, 2000), Image.BILINEAR)
        self.assertEqual(dhsh, dhash_bytes(photo))
        photo = self.photo.resize((90, 90), Image.BILINEAR)
        self.assertEqual(dhsh, dhash_bytes(photo))
