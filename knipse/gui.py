# -*- coding: utf-8 -*-

'''Highly experimental module for the would-be GUI components of knipse'''

import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image
import click


def grid_fill(widget):
    widget.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
    widget.columnconfigure(0, weight=1)
    widget.rowconfigure(0, weight=1)


class ImageDisplay(ttk.Frame):

    def __init__(self, parent, path, **kwargs):
        super().__init__(master=parent, **kwargs)
        self.img = Image.open(path)

        self.tkimg = ImageTk.PhotoImage(self.img.resize((400, 300)))

        canvas = tk.Canvas(self)
        grid_fill(canvas)

        canvas.create_image(0, 0, anchor=tk.NW, image=self.tkimg)


@click.command(name='display')
@click.argument('path',
                type=click.Path(exists=True, file_okay=True, dir_okay=False,
                                resolve_path=True), required=True)
def cli_display(path):
    '''Display the given image on screen.'''
    root = tk.Tk()
    root.title('knipse - display {}'.format(path))

    imgd = ImageDisplay(root, path, padding='5 5 5 5')
    grid_fill(imgd)
    root.bind('<Configure>', print)

    root.mainloop()
