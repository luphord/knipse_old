# -*- coding: utf-8 -*-

import click

from .descriptor import ListDescriptor


class KnipseFieldsReader:
    def __init__(self, fields):
        self.fields = fields

    def __call__(self, obj):
        for field in self.fields:
            if field == '*':
                for any_field in dir(obj):
                    if not any_field.startswith('_'):
                        yield getattr(obj, any_field, None)
            yield getattr(obj, field, None)

    def tab(self, obj):
        return '\t'.join(str(v) for v in self(obj))


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
    lists = [int(obj[1:] if obj.upper().startswith('L') else int(obj))
             for obj in list_id]
    for list_id in lists:
        descr = ListDescriptor(list_id, None, '')
        for list_entry, img in db.load_list_entries(descr):
            click.echo(fields.tab(img))


@click.command(name='show-image')
@click.option('-f', '--fields', type=FIELDS, default='image_id;path',
              show_default=True,
              help='fields of knipse object to output')
@click.argument('image-id', type=click.STRING, nargs=-1)
@click.pass_context
def cli_show_image(ctx, fields, image_id):
    '''Show images corresponding to `image_id`(s)'''
    db = ctx.obj['database']
    images = [int(obj[1:]) if obj.upper().startswith('I') else int(obj)
              for obj in image_id]
    for image_id in images:
        click.echo(fields.tab(db.load_image(image_id)))
    if not image_id:
        for img in db.load_all_images():
            click.echo(fields.tab(img))
