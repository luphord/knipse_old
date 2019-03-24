# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime


class ImageDescriptor:
    '''Container for image metadata'''

    def __init__(self,
                 path: Path,
                 creation_date: datetime,
                 dhash: bytes) -> None:
        self.path = Path(path)
        self.creation_date = creation_date
        self.dhash = dhash

    def __repr__(self) -> str:
        return '''ImageDescriptor('{}', {!r}, {})'''.format(
            self.path, self.creation_date, self.dhash)
