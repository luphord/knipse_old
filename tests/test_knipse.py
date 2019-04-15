#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `knipse` package."""


import unittest
from click.testing import CliRunner

from knipse import cli


class TestKnipse(unittest.TestCase):
    """Tests for `knipse` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
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
