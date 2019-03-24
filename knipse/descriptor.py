# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime


class ImageDescriptor:
    '''Container for image metadata'''

    def __init__(self,
                 path: Path,
                 created_at: datetime,
                 dhash: bytes) -> None:
        self.path = Path(path)
        self.created_at = created_at
        self.dhash = dhash

    def __repr__(self) -> str:
        return '''ImageDescriptor('{}', {!r}, {})'''.format(
            self.path, self.created_at, self.dhash)
