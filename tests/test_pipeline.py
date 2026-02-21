"""Tests für eraa_visualizer.pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_run_pipeline_returns_list():
    """run_pipeline() liefert eine Liste von Pfaden (ggf. leer)."""
    from eraa_visualizer.pipeline import run_pipeline
    result = run_pipeline()
    assert isinstance(result, list)
    for p in result:
        assert hasattr(p, "exists")


def test_run_pipeline_with_config_path(project_root):
    """run_pipeline(config_path) läuft durch."""
    from eraa_visualizer.pipeline import run_pipeline
    path = project_root / "config.yaml"
    if not path.exists():
        pytest.skip("config.yaml not found")
    result = run_pipeline(path)
    assert isinstance(result, list)
