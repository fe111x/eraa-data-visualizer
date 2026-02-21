"""Pytest fixtures für ERAA Data Visualizer."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest

# Projektroot für Imports (src muss im Pfad sein)
import sys
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def project_root() -> Path:
    return ROOT


@pytest.fixture
def config():
    from eraa_visualizer.config import Config
    cfg = Config.load(ROOT / "config.yaml")
    return cfg


@pytest.fixture
def config_empty():
    from eraa_visualizer.config import Config
    return Config()


@pytest.fixture
def df_adequacy() -> pd.DataFrame:
    return pd.DataFrame({
        "study_zone": ["AT00", "AT00", "BE00"],
        "target_year": [2025, 2025, 2025],
        "scenario": ["A", "A", "A"],
        "climate_year": [1, 2, 1],
        "sample_id": [1, 1, 1],
        "lole": [0.5, 1.2, 2.0],
        "eens": [0.1, 0.3, 0.5],
        "lld": [0, 2, 3],
        "ens": [0.05, 0.15, 0.25],
        "p50_lld": [0, 0, 0],
        "p95_lld": [1, 3, 5],
        "p50_ens": [0, 0, 0],
        "p95_ens": [0.1, 0.2, 0.4],
    })


@pytest.fixture
def df_adequacy_hour_month() -> pd.DataFrame:
    rows = []
    for zone in ["AT00", "BE00"]:
        for ty in [2025]:
            for month in [1, 6, 12]:
                for hour in [0, 12]:
                    rows.append({
                        "study_zone": zone,
                        "target_year": ty,
                        "climate_year": 1,
                        "sample_id": 1,
                        "month": month,
                        "hour": hour,
                        "lole_h": 0.01,
                        "ens_mwh": 0.5,
                    })
    return pd.DataFrame(rows)


@pytest.fixture
def df_dispatch() -> pd.DataFrame:
    return pd.DataFrame({
        "study_zone": ["DE00", "DE00"],
        "target_year": [2025, 2025],
        "technology": ["Wind Onshore", "Solar"],
        "datetime": ["2025-01-15T08:00:00", "2025-06-15T12:00:00"],
        "climate_year": [1, 1],
        "sample_id": [1, 1],
        "generation_mw": [1000.0, 500.0],
        "load_mw": [0.0, 0.0],
    })


@pytest.fixture
def df_net_position() -> pd.DataFrame:
    return pd.DataFrame({
        "study_zone": ["DE00", "FR00"],
        "target_year": [2025, 2025],
        "datetime": ["2025-01-15T08:00:00", "2025-01-15T18:00:00"],
        "climate_year": [1, 1],
        "sample_id": [1, 1],
        "net_position_mw": [500.0, -200.0],
    })


@pytest.fixture
def df_prices() -> pd.DataFrame:
    return pd.DataFrame({
        "study_zone": ["DE00", "DE00"],
        "target_year": [2025, 2025],
        "datetime": ["2025-01-15T08:00:00", "2025-01-15T18:00:00"],
        "climate_year": [1, 1],
        "sample_id": [1, 1],
        "price_eur_mwh": [80.0, 120.0],
    })


@pytest.fixture
def df_storage() -> pd.DataFrame:
    return pd.DataFrame({
        "study_zone": ["DE00"],
        "target_year": [2025],
        "storage_type": ["Battery"],
        "datetime": ["2025-01-15T12:00:00"],
        "climate_year": [1],
        "sample_id": [1],
        "level_pct": [65.0],
        "level_mwh": [650.0],
    })


@pytest.fixture
def temp_data_dir(tmp_path):
    """Temporäres Verzeichnis mit Beispieldaten (CSV)."""
    (tmp_path / "adequacy.csv").write_text(
        "study_zone,target_year,scenario,climate_year,sample_id,lole,eens,lld,ens,p50_lld,p95_lld,p50_ens,p95_ens\n"
        "AT00,2025,A,1,1,0.5,0.1,0,0.05,0,1,0,0.1\n"
        "BE00,2025,A,1,1,1.2,0.2,1,0.1,0,2,0,0.2\n",
        encoding="utf-8",
    )
    (tmp_path / "adequacy_hour_month.csv").write_text(
        "study_zone,target_year,climate_year,sample_id,month,hour,lole_h,ens_mwh\n"
        "AT00,2025,1,1,1,8,0.01,0.5\n"
        "AT00,2025,1,1,6,12,0.005,0.3\n",
        encoding="utf-8",
    )
    (tmp_path / "dispatch.csv").write_text(
        "study_zone,target_year,technology,datetime,climate_year,sample_id,generation_mw,load_mw\n"
        "DE00,2025,Wind Onshore,2025-01-15T08:00:00,1,1,1000,0\n"
        "DE00,2025,Solar,2025-06-15T12:00:00,1,1,500,0\n",
        encoding="utf-8",
    )
    return tmp_path
