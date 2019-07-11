# -*- coding: utf-8 -*-

import click

from .descriptor import ListDescriptor


@click.command(name='show')
@click.argument('knipse-object', type=click.STRING, nargs=-1)
@click.pass_context
def cli_show(ctx, knipse_object):
    '''Show `knipse-object`(s) like lists or images'''
    db = ctx.obj['database']
    lists = [int(obj[1:])
             for obj in knipse_object
             if obj.upper().startswith('L')]
    for list_id in lists:
        for img in db.load_list_entries(ListDescriptor(list_id, None, '')):
            click.echo(img)
    images = [int(obj[1:])
              for obj in knipse_object
              if obj.upper().startswith('I')]
    for image_id in images:
        click.echo(db.load_image(image_id))
    if not knipse_object:
        for img in db.load_all_images():
            click.echo(img)
