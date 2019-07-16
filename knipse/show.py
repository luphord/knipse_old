# -*- coding: utf-8 -*-

from types import MethodType

import click

from .descriptor import ListDescriptor


def getattr_multiple(field, *obj):
    for o in obj:
        v = getattr(o, field, None)
        if v is not None:
            return v
    return None


def dir_multiple(*obj):
    fields = set([])
    for o in obj:
        for field in dir(o):
            if not field.startswith('_') \
                    and field not in fields \
                    and not isinstance(getattr(o, field), MethodType):
                fields.add(field)
                yield field


class KnipseFieldsReader:
    def __init__(self, fields):
        self.fields = fields

    def __call__(self, *obj):
        for field in self.headers(*obj):
            yield getattr_multiple(field, *obj)

    def headers(self, *obj):
        for field in self.fields:
            if field == '*':
                yield from dir_multiple(*obj)
            else:
                yield field

    def tab(self, *obj):
        return '\t'.join(str(v) for v in self(*obj))

    def headers_tab(self, *obj):
        return '\t'.join(str(v) for v in self.headers(*obj))


class KnipseFields(click.ParamType):
    '''Parameter type a list of fields (separated by semicolon)'''
    name = 'fields'

    def convert(self, value, param, ctx):
        try:
            return KnipseFieldsReader([f.strip() for f in value.split(';')])
        except ValueError:
            self.fail('{} is not a fields format'.format(value), param, ctx)


FIELDS = KnipseFields()


@click.command(name='show-list')
@click.option('-f', '--fields', type=FIELDS, default='image_id;path',
              show_default=True,
              help='fields of knipse object to output')
@click.argument('list-id', type=click.STRING, nargs=-1)
@click.pass_context
def cli_show_list(ctx, fields, list_id):
    '''Show lists corresponding to `list_id`(s)'''
    db = ctx.obj['database']
    list_ids = [int(obj[1:] if obj.upper().startswith('L') else int(obj))
                for obj in list_id]
    lists = [db.load_list_entries(ListDescriptor(list_id, None, ''))
             for list_id in list_ids]
    for lst in lists:
        for list_entry, img in lst:
            click.echo(fields.tab(list_entry, img))


@click.command(name='show-image')
@click.option('-f', '--fields', type=FIELDS, default='image_id;path',
              show_default=True,
              help='fields of knipse object to output')
@click.option('-h', '--header/--no-header', default=False,
              show_default=True,
              help='print column headers')
@click.argument('image-id', type=click.STRING, nargs=-1)
@click.pass_context
def cli_show_image(ctx, fields, header, image_id):
    '''Show images corresponding to `image_id`(s)'''
    db = ctx.obj['database']
    if not image_id:
        images = list(db.load_all_images())
    else:
        image_ids = [int(obj[1:])
                     if obj.upper().startswith('I')
                     else int(obj)
                     for obj in image_id]
        images = [db.load_image(img_id) for img_id in image_ids]
    if header:
        click.echo(fields.headers_tab(images[0] if images else None))
    for image in images:
        click.echo(fields.tab(image))
