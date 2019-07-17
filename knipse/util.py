# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime
from types import MethodType

import click


def get_modification_time(path: Path) -> datetime:
    # getmtime does not support Path in Python 3.5 -> need to convert to str
    return datetime.fromtimestamp(os.path.getmtime(str(path)))


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
