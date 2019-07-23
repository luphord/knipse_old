# -*- coding: utf-8 -*-

'''GUI experiments with kivy'''

from itertools import islice
from typing import Iterable
from pathlib import Path

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
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
                    node = TreeViewLabel(text=parent.name)
                    nodes[parent] = tree.add_node(node, nodes[parent.parent])
            node = TreeViewLabel(text=img.path.name)
            tree.add_node(node, nodes[img.path.parent])
        self.add_widget(tree)


class KnipseApp(App):

    def __init__(self, db: KnipseDB, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db

    def build(self):
        master_layout = BoxLayout(orientation='horizontal', padding=10)
        tree = FolderTreeWidget('My Collection', self.db, size_hint=(0.3, 1))
        master_layout.add_widget(tree)
        images_layout = BoxLayout(orientation='vertical', size_hint=(0.7, 1))
        master_layout.add_widget(images_layout)
        for img in islice(self.db.load_all_images(), 5):
            text = '{} {}'.format(img.image_id, img.path)
            images_layout.add_widget(Label(text=text))
        return master_layout
