# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime


def get_modification_time(path: Path) -> datetime:
    # getmtime does not support Path in Python 3.5 -> need to convert to str
    return datetime.fromtimestamp(os.path.getmtime(str(path)))
