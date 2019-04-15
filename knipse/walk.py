# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime
from typing import List, Callable, Optional, Iterable, Tuple  # noqa: 401

import click
from PIL import Image

from .image import descriptor_from_image
from .util import get_modification_time


_files_to_folders_heuristic = 0.1


def walk_images(base_folder: Path,
                filter: Optional[Callable[[Path, Path, datetime], bool]]
                = None) \
        -> Iterable[Tuple[Path, Image.Image, float]]:
    '''Walk all folders below `base_folder` and yield contained images'''
    folder_tree = [[(Path(base_folder).resolve(), 0.0, 1.0)]]
    while folder_tree:
        level = folder_tree.pop()
        folder, lower, higher = level.pop()
        files = []
        sub_folders = []  # type: List[Path]
        for entry in folder.iterdir():
            if entry.is_file():
                files.append(entry)
            elif entry.is_dir():
                sub_folders.append(entry)
            else:
                raise Exception('Unexpected folder entry {}'.format(entry))
        n_sub_folders = len(sub_folders)
        file_ratio = _files_to_folders_heuristic \
            / (n_sub_folders + _files_to_folders_heuristic)
        files_increase = (higher - lower) * file_ratio
        if not files:
            files_increase = 0
        local_higher = lower + files_increase
        local_progress = 0.0
        for file_path in files:
            local_progress += 1 / len(files)
            try:
                progress = lower + (local_higher - lower) * local_progress
                mtime = get_modification_time(file_path)
                if not filter or filter(base_folder, file_path, mtime):
                    img = Image.open(file_path)
                    yield file_path, img, progress
            except IOError:
                pass  # not an image
        if level:
            folder_tree.append(level)
        if sub_folders:
            folder_increase = (higher - lower - files_increase) / n_sub_folders
            folder_progr = [(folder,
                             lower + files_increase + i * folder_increase,
                             lower + files_increase + (i+1) * folder_increase)
                            for i, folder in enumerate(sub_folders)]
            folder_progr.reverse()  # by popping the list we walk backwards
            folder_tree.append(folder_progr)


@click.command(name='walk')
@click.argument('base_folder',
                type=click.Path(exists=True, file_okay=False, dir_okay=True,
                                resolve_path=True), default='.')
def cli_walk(base_folder):
    '''Recursively list all images below `base_folder`'''
    for file_path, img, progress in walk_images(base_folder):
        descr = descriptor_from_image(base_folder, file_path, img)
        click.echo('{:.1f}%\t{}'.format(progress * 100, descr))
