"""Tests für eraa_visualizer.loaders."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_load_adequacy(temp_data_dir):
    from eraa_visualizer.loaders import load_adequacy
    from eraa_visualizer.config import Config
    cfg = Config()
    cfg.paths.data_dir = str(temp_data_dir)
    schema = getattr(cfg.schema, "adequacy", None) or {}
    df = load_adequacy(Path(temp_data_dir), schema)
    assert df is not None
    assert not df.empty
    assert "lole" in df.columns
    assert "study_zone" in df.columns


def test_load_adequacy_hour_month(temp_data_dir):
    from eraa_visualizer.loaders import load_adequacy_hour_month
    df = load_adequacy_hour_month(Path(temp_data_dir))
    assert df is not None
    assert not df.empty
    assert "month" in df.columns
    assert "hour" in df.columns
    assert "lole_h" in df.columns or "ens_mwh" in df.columns


def test_load_dispatch(temp_data_dir):
    from eraa_visualizer.loaders import load_dispatch
    from eraa_visualizer.config import Config
    cfg = Config()
    schema = getattr(cfg.schema, "dispatch", None) or {}
    df = load_dispatch(Path(temp_data_dir), schema)
    assert df is not None
    assert not df.empty
    assert "generation_mw" in df.columns


def test_load_dataset_with_temp_dir(temp_data_dir):
    from eraa_visualizer.loaders import load_dataset
    from eraa_visualizer.config import Config, PathsConfig
    cfg = Config(paths=PathsConfig(data_dir=str(temp_data_dir), output_dir="output"))
    dataset = load_dataset(cfg)
    assert dataset is not None
    assert dataset.adequacy is not None
    assert dataset.dispatch is not None
    assert dataset.adequacy_hour_month is not None


def test_load_dataset_empty_dir(tmp_path):
    from eraa_visualizer.loaders import load_dataset
    from eraa_visualizer.config import Config, PathsConfig
    cfg = Config(paths=PathsConfig(data_dir=str(tmp_path), output_dir=str(tmp_path)))
    dataset = load_dataset(cfg)
    assert dataset.adequacy is None
    assert dataset.dispatch is None
    assert dataset.adequacy_hour_month is None
