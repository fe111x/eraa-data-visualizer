"""Tests für eraa_visualizer.models."""

from __future__ import annotations

import pandas as pd
import pytest

from eraa_visualizer.models import (
    ERAADataset,
    adequacy_from_dataframe,
    dispatch_from_dataframe,
    net_position_from_dataframe,
    prices_from_dataframe,
    storage_from_dataframe,
)


def test_adequacy_from_dataframe_identity(df_adequacy):
    out = adequacy_from_dataframe(df_adequacy)
    assert out is not None
    assert "lole" in out.columns
    assert "ens" in out.columns
    assert "study_zone" in out.columns
    assert len(out) == len(df_adequacy)


def test_adequacy_from_dataframe_rename():
    df = pd.DataFrame({
        "StudyZone": ["AT00"],
        "target_year": [2025],
        "scenario": ["A"],
        "climate_year": [1],
        "sample_id": [1],
        "lole": [1.0],
        "eens": [0.1],
        "lld": [0],
        "ens": [0.05],
        "p50_lld": [0],
        "p95_lld": [1],
        "p50_ens": [0],
        "p95_ens": [0.1],
    })
    out = adequacy_from_dataframe(df, schema={"study_zone": "StudyZone"})
    assert "study_zone" in out.columns
    assert out["study_zone"].iloc[0] == "AT00"


def test_dispatch_from_dataframe(df_dispatch):
    out = dispatch_from_dataframe(df_dispatch)
    assert "generation_mw" in out.columns
    assert "technology" in out.columns
    assert "datetime" in out.columns
    assert len(out) == len(df_dispatch)


def test_net_position_from_dataframe(df_net_position):
    out = net_position_from_dataframe(df_net_position)
    assert "net_position_mw" in out.columns
    assert "study_zone" in out.columns


def test_prices_from_dataframe(df_prices):
    out = prices_from_dataframe(df_prices)
    assert "price_eur_mwh" in out.columns


def test_storage_from_dataframe(df_storage):
    out = storage_from_dataframe(df_storage)
    assert "level_pct" in out.columns
    assert "storage_type" in out.columns


def test_eraa_dataset_empty():
    ds = ERAADataset()
    assert ds.adequacy is None
    assert ds.dispatch is None
    assert ds.net_position is None
    assert ds.prices is None
    assert ds.storage is None
    assert ds.adequacy_hour_month is None


def test_eraa_dataset_with_data(df_adequacy, df_dispatch):
    ds = ERAADataset(adequacy=df_adequacy, dispatch=df_dispatch)
    assert ds.adequacy is not None
    assert len(ds.adequacy) == len(df_adequacy)
    assert ds.dispatch is not None
    assert ds.net_position is None
