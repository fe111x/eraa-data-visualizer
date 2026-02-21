"""Laden von ERAA-Output-Daten aus CSV/Parquet mit Schema-Mapping."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import Config
from .models import (
    ERAADataset,
    adequacy_from_dataframe,
    dispatch_from_dataframe,
    net_position_from_dataframe,
    prices_from_dataframe,
    storage_from_dataframe,
)


def _read_table(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    suf = path.suffix.lower()
    if suf == ".csv":
        return pd.read_csv(path)
    if suf in (".parquet", ".pq"):
        return pd.read_parquet(path)
    return None


def load_adequacy(data_dir: Path, schema: dict[str, str]) -> pd.DataFrame | None:
    for name in ("adequacy.csv", "adequacy.parquet", "lole_ens.csv"):
        df = _read_table(data_dir / name)
        if df is not None:
            return adequacy_from_dataframe(df, schema)
    return None


def load_dispatch(data_dir: Path, schema: dict[str, str]) -> pd.DataFrame | None:
    for name in ("dispatch.csv", "dispatch.parquet", "generation.csv"):
        df = _read_table(data_dir / name)
        if df is not None:
            return dispatch_from_dataframe(df, schema)
    return None


def load_net_position(data_dir: Path, schema: dict[str, str]) -> pd.DataFrame | None:
    for name in ("net_position.csv", "net_position.parquet", "netpositions.csv"):
        df = _read_table(data_dir / name)
        if df is not None:
            return net_position_from_dataframe(df, schema)
    return None


def load_prices(data_dir: Path, schema: dict[str, str]) -> pd.DataFrame | None:
    for name in ("prices.csv", "prices.parquet"):
        df = _read_table(data_dir / name)
        if df is not None:
            return prices_from_dataframe(df, schema)
    return None


def load_storage(data_dir: Path, schema: dict[str, str]) -> pd.DataFrame | None:
    for name in ("storage.csv", "storage.parquet", "storage_levels.csv"):
        df = _read_table(data_dir / name)
        if df is not None:
            return storage_from_dataframe(df, schema)
    return None


def load_adequacy_hour_month(data_dir: Path) -> pd.DataFrame | None:
    """Lädt Adequacy nach Stunde/Monat (Spalten: study_zone, target_year, month, hour, ggf. climate_year, sample_id, lole_h, ens_mwh)."""
    for name in ("adequacy_hour_month.csv", "adequacy_hour_month.parquet"):
        df = _read_table(data_dir / name)
        if df is not None:
            return df
    return None


def load_dataset(config: Config | None = None) -> ERAADataset:
    """Lädt alle verfügbaren ERAA-Daten aus config.paths.data_dir."""
    config = config or Config.load()
    data_dir = Path(config.paths.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    s = config.schema
    return ERAADataset(
        adequacy=load_adequacy(data_dir, s.adequacy),
        adequacy_hour_month=load_adequacy_hour_month(data_dir),
        dispatch=load_dispatch(data_dir, s.dispatch),
        net_position=load_net_position(data_dir, s.net_position),
        prices=load_prices(data_dir, s.prices),
        storage=load_storage(data_dir, s.storage),
    )
