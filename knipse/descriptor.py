# -*- coding: utf-8 -*-

from pathlib import Path


class ImageDescriptor:
    '''Container for image metadata'''

    def __init__(self, path, creation_date, dhash):
        self.path = Path(path)
        self.creation_date = creation_date
        self.dhash = dhash

    def __repr__(self):
        return '''ImageDescriptor('{}', {!r}, {})'''.format(
            self.path, self.creation_date, self.dhash)
