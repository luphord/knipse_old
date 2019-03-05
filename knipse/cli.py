# -*- coding: utf-8 -*-

"""Console script for knipse."""
import sys
import click
from .dhash import cli_dhash
from .walk import cli_walk


@click.group(name='knipse')
def cli_knipse():
    '''Manage your photo collections and lists.'''
    return 0


cli_knipse.add_command(cli_dhash)
cli_knipse.add_command(cli_walk)


if __name__ == "__main__":
    sys.exit(cli_knipse())
