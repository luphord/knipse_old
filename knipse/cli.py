# -*- coding: utf-8 -*-

"""Console script for knipse."""
import sys
import click
from .dhash import cli_dhash


@click.group(name='knipse')
def cli_knipse():
    '''Manage your photo collections and lists.'''
    return 0


cli_knipse.add_command(cli_dhash)


if __name__ == "__main__":
    sys.exit(cli_knipse())
