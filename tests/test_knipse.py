#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from click.testing import CliRunner

from knipse import cli


class TestKnipse(unittest.TestCase):

    def test_command_line_interface(self):
        '''Test command line interface.'''
        runner = CliRunner()
        result = runner.invoke(cli.cli_knipse)
        assert result.exit_code == 0
        assert 'photo' in result.output
        help_result = runner.invoke(cli.cli_knipse, ['--help'])
        assert help_result.exit_code == 0
        # number of spaces between `--help` and rest may change as further
        # options are added to the cli (-> separate assertions)
        assert '--help' in help_result.output
        assert 'Show this message and exit.' in help_result.output
