# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""CLI tests."""

from __future__ import absolute_import, print_function

import os

from click.testing import CliRunner

from invenio_circulation.cli import diagram


def test_cli_diagram(script_info, diagram_file_name):
    """."""
    runner = CliRunner()

    result = runner.invoke(
        diagram, [diagram_file_name], obj=script_info)
    assert result.exit_code == 0
    assert os.path.isfile(diagram_file_name)
