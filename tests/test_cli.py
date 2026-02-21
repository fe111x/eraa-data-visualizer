"""Tests für eraa_visualizer.cli."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

# Ensure src is on path
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_cli_list_only(tmp_path):
    from eraa_visualizer.cli import main
    runner = CliRunner()
    result = runner.invoke(main, ["--list-only", "--config", str(ROOT / "config.yaml")])
    assert result.exit_code == 0
    assert "Adequacy" in result.output or "Dispatch" in result.output or "Geladene" in result.output


def test_cli_help():
    from eraa_visualizer.cli import main
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "config" in result.output.lower()
    assert "list-only" in result.output
