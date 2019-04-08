# -*- coding: utf-8 -*-

'''Highly experimental module for the would-be GUI components of knipse'''

import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image
import click


def grid_fill(widget, parent):
    widget.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(0, weight=1)


class ImageDisplay(ttk.Frame):

    def __init__(self, parent, path, **kwargs):
        super().__init__(master=parent, **kwargs)
        self.img = Image.open(path)
        self.imgid = None
        self.canvas = tk.Canvas(self)
        grid_fill(self.canvas, self)
        self.bind('<Configure>', self.on_resize)

    def display(self, width, height):
        resized_img = self.img.resize((width, height))
        self.tkimg = ImageTk.PhotoImage(resized_img)
        if self.imgid is not None:
            self.canvas.delete(self.imgid)
        self.imgid = self.canvas.create_image(0, 0, anchor=tk.NW,
                                              image=self.tkimg)

    def on_resize(self, evt):
        self.display(evt.width, evt.height)


@click.command(name='display')
@click.argument('path',
                type=click.Path(exists=True, file_okay=True, dir_okay=False,
                                resolve_path=True), required=True)
def cli_display(path):
    '''Display the given image on screen.'''
    root = tk.Tk()
    root.title('knipse - display {}'.format(path))

    imgd = ImageDisplay(root, path, padding='5 5 5 5')
    grid_fill(imgd, root)

    root.mainloop()
