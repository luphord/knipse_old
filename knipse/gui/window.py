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


class SelectableTreeViewLabel(TreeViewLabel):
    def __init__(self, *args, **kwargs):
        self.register_event_type('on_path_changed')
        super().__init__(*args, **kwargs)

    def on_touch_down(self, *args):
        self.dispatch('on_path_changed', self.text)

    def on_path_changed(self, *args):
        pass


class FolderTreeWidget(FloatLayout):
    root_label = StringProperty('')
    db = ObjectProperty(None)
    selected_path = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_db(self, *args):
        self._populate(self.root_label, self.db.load_all_images())

    def on_nodes_path_changed(self, node, path):
        self.selected_path = path

    def _populate(self,
                  root_label: str,
                  images: Iterable[ImageDescriptor]):
        tree = TreeView(root_options=dict(text=root_label))
        nodes = {Path('.'): None}
        for img in islice(images, 10):
            for parent in reversed(img.path.parents):
                if parent not in nodes:
                    node = SelectableTreeViewLabel(text=parent.name)
                    node.bind(on_path_changed=self.on_nodes_path_changed)
                    nodes[parent] = tree.add_node(node, nodes[parent.parent])
            node = TreeViewLabel(text=img.path.name)
            tree.add_node(node, nodes[img.path.parent])
        self.add_widget(tree)


class KnipseApp(App):
    selected_path = StringProperty('asd')

    def __init__(self, db: KnipseDB, base_folder: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db
        self.base_folder = base_folder
        self.test_img = str(self.base_folder / self.db.load_image(1).path)

    def on_selected_path(self, *args):
        print('App', *args)
