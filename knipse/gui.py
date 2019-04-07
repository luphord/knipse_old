# -*- coding: utf-8 -*-

'''Highly experimental module for the would-be GUI components of knipse'''

import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image
import click


@click.command(name='display')
@click.argument('path',
                type=click.Path(exists=True, file_okay=True, dir_okay=False,
                                resolve_path=True), required=True)
def cli_display(path):
    '''Display the given image on screen.'''
    root = tk.Tk()
    root.title('knipse - display {}'.format(path))

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

    img = Image.open(path)
    img = img.resize((800, 600))

    tkimg = ImageTk.PhotoImage(img)

    canvas = tk.Canvas(mainframe)
    canvas.pack()
    canvas.create_image(100, 100, image=tkimg)

    root.mainloop()
