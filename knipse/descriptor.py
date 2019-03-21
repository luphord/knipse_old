# -*- coding: utf-8 -*-

from pathlib import Path


class ImageDescriptor:
    '''Container for image metadata'''

    def __init__(self, path, dhash):
        self.path = Path(path)
        self.dhash = dhash

    def __repr__(self):
        return '''ImageDescriptor('{}', {})'''.format(self.path, self.dhash)
