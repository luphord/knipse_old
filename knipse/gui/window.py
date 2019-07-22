# -*- coding: utf-8 -*-

'''GUI experiments with kivy'''

from itertools import islice

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.treeview import TreeView, TreeViewLabel

from ..db import KnipseDB


kivy.require('1.11.0')


class KnipseApp(App):

    def __init__(self, db: KnipseDB, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db

    def build(self):
        layout = GridLayout(cols=1, padding=10)
        tree = TreeView(root_options=dict(text='Collection'))
        tree.add_node(TreeViewLabel(text='My first item'))
        tree.add_node(TreeViewLabel(text='My second item'))
        layout.add_widget(tree)
        for img in islice(self.db.load_all_images(), 10):
            text = '{} {}'.format(img.image_id, img.path)
            layout.add_widget(Label(text=text))
        return layout
