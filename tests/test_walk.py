# -*- coding: utf-8 -*-

import unittest
from pathlib import Path

from knipse.walk import walk_images


class TestImageWalking(unittest.TestCase):

    def setUp(self):
        self.src = Path(__file__).resolve().parent / 'images' / 'various'
        self.expected_images = [
            'img_0002.jpg',
            'folder1/img_0001.jpg',
            'folder1/img_0000.jpg',
            'folder2/img_0010.jpg',
            'folder2/folder4/img_0007.jpg',
            'folder2/folder4/img_0008.jpg',
            'folder2/folder4/img_0009.jpg',
            'folder2/folder3/img_0005.jpg',
            'folder2/folder3/img_0003.jpg',
            'folder2/folder3/img_0006.jpg',
            'folder2/folder3/img_0004.jpg'
        ]

    def test_walking(self):
        '''Test walking images within a folder structure'''
        for file_path, img, progress in walk_images(self.src):
            p = str(file_path.relative_to(self.src))
            self.assertIn(p, self.expected_images)
            self.expected_images.remove(p)
        self.assertEqual(0, len(self.expected_images))
