"""Tests für eraa_visualizer.config."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_config_defaults(config_empty):
    from eraa_visualizer.config import Config
    c = config_empty
    assert c.paths.data_dir == "data"
    assert c.paths.output_dir == "output"
    assert "adequacy" in c.paths.output_subdirs
    assert c.dimensions.n_climate_years == 36
    assert c.dimensions.n_samples_per_climate_year == 10
    assert 2025 in c.dimensions.target_years
    assert c.visualization.figure_width == 1200
    assert c.visualization.template == "plotly_white"


def test_config_load(project_root):
    from eraa_visualizer.config import Config
    path = project_root / "config.yaml"
    if not path.exists():
        pytest.skip("config.yaml not found")
    c = Config.load(path)
    assert c is not None
    assert isinstance(c.paths.data_dir, str)
    assert isinstance(c.dimensions.target_years, list)


def test_config_load_nonexistent():
    from eraa_visualizer.config import Config
    c = Config.load(Path("/nonexistent/config.yaml"))
    assert c is not None
    assert c.paths.data_dir == "data"


def test_config_output_path(config_empty):
    p = config_empty.output_path("adequacy", "test.html")
    assert p.name == "test.html"
    assert "adequacy" in str(p)
    assert p.parent.name == "adequacy"


def test_config_output_path_unknown_category(config_empty):
    p = config_empty.output_path("unknown_cat", "file.html")
    assert p.name == "file.html"
    assert "unknown_cat" in str(p)
