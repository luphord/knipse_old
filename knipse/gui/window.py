# -*- coding: utf-8 -*-

'''GUI experiments with kivy'''

from itertools import islice
from typing import Iterable
from pathlib import Path

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.treeview import TreeView, TreeViewLabel

from ..db import KnipseDB
from ..image import ImageDescriptor


kivy.require('1.11.0')


class FolderTreeWidget(FloatLayout):

    def __init__(self,
                 root_label: str,
                 db: KnipseDB,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._populate(root_label, db.load_all_images())

    def _populate(self,
                  root_label: str,
                  images: Iterable[ImageDescriptor]):
        tree = TreeView(root_options=dict(text=root_label))
        nodes = {Path('.'): None}
        for img in islice(images, 10):
            for parent in reversed(img.path.parents):
                if parent not in nodes:
                    node = TreeViewLabel(text=str(parent))
                    nodes[parent] = tree.add_node(node, nodes[parent.parent])
        self.add_widget(tree)


class KnipseApp(App):

    def __init__(self, db: KnipseDB, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db

    def build(self):
        layout = GridLayout(cols=2, padding=10)
        tree = FolderTreeWidget('My Collection', self.db)
        layout.add_widget(tree)
        for img in islice(self.db.load_all_images(), 1):
            text = '{} {}'.format(img.image_id, img.path)
            layout.add_widget(Label(text=text))
        return layout
