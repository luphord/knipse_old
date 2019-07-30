# -*- coding: utf-8 -*-

'''GUI experiments with kivy'''

from itertools import islice
from typing import Iterable
from pathlib import Path

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.properties import ObjectProperty, StringProperty

from ..db import KnipseDB
from ..image import ImageDescriptor


kivy.require('1.11.0')


class ImageList(BoxLayout):
    db = ObjectProperty(None)
    selected_path = StringProperty('')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, orientation='vertical', **kwargs)

    def _populate(self):
        self.clear_widgets()
        folder = Path(self.selected_path)
        for descr in self.db.load_all_images():
            if descr.path.parent == folder:
                self.add_widget(Label(text=str(descr.path)))

    def on_selected_path(self, *args):
        self._populate()


class SelectableTreeViewLabel(TreeViewLabel):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_event_type('on_path_changed')
        self.path = path

    def on_touch_down(self, *args):
        self.dispatch('on_path_changed', self.path)

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
        self.selected_path = str(path)

    def _populate(self,
                  root_label: str,
                  images: Iterable[ImageDescriptor]):
        tree = TreeView(root_options=dict(text=root_label))
        nodes = {Path('.'): None}
        for img in islice(images, 10):
            for parent in reversed(img.path.parents):
                if parent not in nodes:
                    node = SelectableTreeViewLabel(path=parent,
                                                   text=parent.name)
                    node.bind(on_path_changed=self.on_nodes_path_changed)
                    nodes[parent] = tree.add_node(node, nodes[parent.parent])
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
