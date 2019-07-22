# -*- coding: utf-8 -*-

'''GUI experiments with kivy'''

import kivy
from kivy.app import App
from kivy.uix.label import Label


kivy.require('1.11.0')


class KnipseApp(App):
    def build(self):
        return Label(text='Welcome to Knipse')
