# -*- coding: utf-8 -*-

'''Highly experimental module for the would-be GUI components of knipse'''

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

from PIL import ImageTk, Image
import click


def grid_fill(widget, parent):
    widget.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(0, weight=1)


class ImageDisplay(ttk.Frame):

    def __init__(self, parent, path, wait_refresh_millis=100, **kwargs):
        super().__init__(master=parent, **kwargs)
        self.wait = timedelta(milliseconds=wait_refresh_millis) \
            if wait_refresh_millis else None
        self.last_refresh_call = datetime.now()
        self.refresh_requested = False
        self.img = Image.open(path)
        self.imgid = None
        self.canvas = tk.Canvas(self)
        self.canvas.create_text(10, 10, anchor=tk.NW, fill='black',
                                font=('Helvetica', 10),
                                text='Loading {}...'.format(path))
        self.first = True
        grid_fill(self.canvas, self)
        self.bind('<Configure>', self.on_resize)

    def on_resize(self, evt):
        if self.first:
            self.first = False
            self.after(100, self.on_resize, evt)
            return
        if self.wait:
            self.width = evt.width
            self.height = evt.height
            self.throttled_display()
        else:
            self.display(evt.width, evt.height)

    def throttled_display(self):
        '''Calls `display` but delays until `self.wait` milliseconds
           if the last request was too recent
        '''
        if self.last_refresh_call + self.wait <= datetime.now():
            self.last_refresh_call = datetime.now()
            self.refresh_requested = False
            self.display(self.width, self.height)
        else:
            if not self.refresh_requested:
                self.refresh_requested = True
                millis = int(self.wait.total_seconds() * 1000)
                self.after(millis, self.throttled_display)

    def display(self, width, height):
        '''Displays the image with a new given width and height.
           This method is intended to be regularly called on resize.
        '''
        self.img.load()  # takes time on first run, no-op afterwards
        ratio = min(width/self.img.size[0], height/self.img.size[1])
        new_size = (int(ratio * self.img.size[0]),
                    int(ratio * self.img.size[1]))
        if new_size[0] <= 0 or new_size[1] <= 0:
            return  # avoid exception on resizing
        resized_img = self.img.resize(new_size)
        self.tkimg = ImageTk.PhotoImage(resized_img)
        if self.imgid is not None:
            self.canvas.delete(self.imgid)
        self.imgid = self.canvas.create_image(0, 0, anchor=tk.NW,
                                              image=self.tkimg)


@click.command(name='display')
@click.argument('path',
                type=click.Path(exists=True, file_okay=True, dir_okay=False,
                                resolve_path=True), required=True)
def cli_display(path):
    '''Display the given image on screen.'''
    root = tk.Tk()
    root.title('knipse - display {}'.format(path))

    imgd = ImageDisplay(root, path, wait_refresh_millis=50, padding='5 5 5 5')
    grid_fill(imgd, root)

    root.mainloop()


@click.command(name='kivy')
@click.pass_context
def cli_kivy(ctx):
    '''Experiment with kivy.'''
    from .window import KnipseApp
    db = ctx.obj['database']
    base_folder = ctx.obj['source']
    KnipseApp(db, base_folder).run()
