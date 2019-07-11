# -*- coding: utf-8 -*-

import click

from .descriptor import ListDescriptor


class KnipseFieldsReader:
    def __init__(self, fields):
        self.fields = fields

    def __call__(self, obj):
        for field in self.fields:
            yield getattr(obj, field, None)

    def tab(self, obj):
        return '\t'.join(str(v) for v in self(obj))


class KnipseFields(click.ParamType):
    '''Parameter type a list of fields (separated by semicolon)'''
    name = 'fields'

    def convert(self, value, param, ctx):
        try:
            return KnipseFieldsReader(value.split(';'))
        except ValueError:
            self.fail('{} is not a fields format'.format(value), param, ctx)


FIELDS = KnipseFields()


@click.command(name='show')
@click.option('-f', '--fields', type=FIELDS, default='image_id;path',
              show_default=True,
              help='fields of knipse object to output')
@click.argument('knipse-object', type=click.STRING, nargs=-1)
@click.pass_context
def cli_show(ctx, fields, knipse_object):
    '''Show `knipse-object`(s) like lists or images'''
    db = ctx.obj['database']
    lists = [int(obj[1:])
             for obj in knipse_object
             if obj.upper().startswith('L')]
    for list_id in lists:
        for img in db.load_list_entries(ListDescriptor(list_id, None, '')):
            click.echo(fields.tab(img))
    images = [int(obj[1:])
              for obj in knipse_object
              if obj.upper().startswith('I')]
    for image_id in images:
        click.echo(fields.tab(db.load_image(image_id)))
    if not knipse_object:
        for img in db.load_all_images():
            click.echo(fields.tab(img))
