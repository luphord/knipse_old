# -*- coding: utf-8 -*-

'''GUI experiments with kivy'''

from itertools import islice
from typing import Iterable
from pathlib import Path

import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.properties import ObjectProperty, StringProperty

from ..db import KnipseDB
from ..image import ImageDescriptor


kivy.require('1.11.0')


class FolderTreeWidget(FloatLayout):
    root_label = StringProperty('')
    db = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_db(self, *args):
        self._populate(self.root_label, self.db.load_all_images())

    def _populate(self,
                  root_label: str,
                  images: Iterable[ImageDescriptor]):
        tree = TreeView(root_options=dict(text=root_label))
        nodes = {Path('.'): None}
        for img in islice(images, 10):
            for parent in reversed(img.path.parents):
                if parent not in nodes:
                    node = TreeViewLabel(text=parent.name)
                    nodes[parent] = tree.add_node(node, nodes[parent.parent])
            node = TreeViewLabel(text=img.path.name)
            tree.add_node(node, nodes[img.path.parent])
        self.add_widget(tree)


class KnipseApp(App):

    def __init__(self, db: KnipseDB, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db
