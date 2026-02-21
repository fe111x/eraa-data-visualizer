"""
Generisches Datenmodell für ERAA-Modelloutputs.

Beschreibt die klassischen Output-Daten eines Adequacy/Dispatch-Modells:
- Adequacy: LOLE, ENS, EENS, LLD, Perzentile (pro Zone, Klimajahr, Sample)
- Economic Dispatch: Erzeugung/Laden nach Technologie (PEMMDB-Typen)
- Net Position: pro Marktgebiet
- Preise: pro Zone/Hub
- Speicher: Füllstände pro Speichertyp

Dimensionen: target_year, climate_year, sample_id (z.B. 36 × 10 = 360 Läufe).
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from pydantic import BaseModel, Field


# --- Adequacy ---
class AdequacyRecord(BaseModel):
    """Eine Zeile Adequacy-Output: LOLE, ENS etc. pro Zone/Klimajahr/Sample."""

    study_zone: str
    target_year: int
    scenario: str = ""
    climate_year: int
    sample_id: int
    lole: float = Field(description="Loss of Load Expectation [h/year]")
    eens: float = Field(description="Expected Energy Not Served [GWh]")
    lld: float = Field(description="Loss of Load Duration [h] (für diese Stichprobe)")
    ens: float = Field(description="Energy Not Served [GWh] (für diese Stichprobe)")
    p50_lld: float | None = None
    p95_lld: float | None = None
    p50_ens: float | None = None
    p95_ens: float | None = None

    class Config:
        extra = "allow"


def adequacy_from_dataframe(df: pd.DataFrame, schema: dict[str, str] | None = None) -> pd.DataFrame:
    """Stellt sicher, dass df die erwarteten Adequacy-Spalten hat; benennt ggf. um."""
    default = {
        "study_zone": "study_zone",
        "target_year": "target_year",
        "scenario": "scenario",
        "climate_year": "climate_year",
        "sample_id": "sample_id",
        "lole": "lole",
        "eens": "eens",
        "lld": "lld",
        "ens": "ens",
        "p50_lld": "p50_lld",
        "p95_lld": "p95_lld",
        "p50_ens": "p50_ens",
        "p95_ens": "p95_ens",
    }
    schema = schema or default
    rename = {v: k for k, v in schema.items() if v in df.columns and v != k}
    if rename:
        df = df.rename(columns=rename)
    return df


# --- Economic Dispatch ---
class DispatchRecord(BaseModel):
    """Erzeugung oder Ladung (z.B. Pumpspeicher/Batterie) pro Zeitschritt/Technologie."""

    study_zone: str
    target_year: int
    technology: str
    datetime: str | int  # ISO datetime oder hour_index
    climate_year: int
    sample_id: int
    generation_mw: float = 0.0
    load_mw: float = 0.0  # z.B. Pumpen-Laden

    class Config:
        extra = "allow"


def dispatch_from_dataframe(df: pd.DataFrame, schema: dict[str, str] | None = None) -> pd.DataFrame:
    default = {
        "study_zone": "study_zone",
        "target_year": "target_year",
        "technology": "technology",
        "datetime": "datetime",
        "climate_year": "climate_year",
        "sample_id": "sample_id",
        "generation_mw": "generation_mw",
        "load_mw": "load_mw",
    }
    schema = schema or default
    rename = {v: k for k, v in schema.items() if v in df.columns and v != k}
    if rename:
        df = df.rename(columns=rename)
    return df


# --- Net Position ---
class NetPositionRecord(BaseModel):
    """Netto-Position (Import/Export) pro Marktgebiet und Zeitschritt."""

    study_zone: str
    target_year: int
    datetime: str | int
    climate_year: int
    sample_id: int
    net_position_mw: float = 0.0

    class Config:
        extra = "allow"


def net_position_from_dataframe(df: pd.DataFrame, schema: dict[str, str] | None = None) -> pd.DataFrame:
    default = {
        "study_zone": "study_zone",
        "target_year": "target_year",
        "datetime": "datetime",
        "climate_year": "climate_year",
        "sample_id": "sample_id",
        "net_position_mw": "net_position_mw",
    }
    schema = schema or default
    rename = {v: k for k, v in schema.items() if v in df.columns and v != k}
    if rename:
        df = df.rename(columns=rename)
    return df


# --- Prices ---
class PriceRecord(BaseModel):
    """Strompreis pro Zone und Zeitschritt [€/MWh]."""

    study_zone: str
    target_year: int
    datetime: str | int
    climate_year: int
    sample_id: int
    price_eur_mwh: float = 0.0

    class Config:
        extra = "allow"


def prices_from_dataframe(df: pd.DataFrame, schema: dict[str, str] | None = None) -> pd.DataFrame:
    default = {
        "study_zone": "study_zone",
        "target_year": "target_year",
        "datetime": "datetime",
        "climate_year": "climate_year",
        "sample_id": "sample_id",
        "price_eur_mwh": "price_eur_mwh",
    }
    schema = schema or default
    rename = {v: k for k, v in schema.items() if v in df.columns and v != k}
    if rename:
        df = df.rename(columns=rename)
    return df


# --- Storage (Füllstände) ---
class StorageRecord(BaseModel):
    """Speicherfüllstand pro Typ und Zeitschritt."""

    study_zone: str
    target_year: int
    storage_type: str
    datetime: str | int
    climate_year: int
    sample_id: int
    level_pct: float | None = None  # 0–100
    level_mwh: float | None = None

    class Config:
        extra = "allow"


def storage_from_dataframe(df: pd.DataFrame, schema: dict[str, str] | None = None) -> pd.DataFrame:
    default = {
        "study_zone": "study_zone",
        "target_year": "target_year",
        "storage_type": "storage_type",
        "datetime": "datetime",
        "climate_year": "climate_year",
        "sample_id": "sample_id",
        "level_pct": "level_pct",
        "level_mwh": "level_mwh",
    }
    schema = schema or default
    rename = {v: k for k, v in schema.items() if v in df.columns and v != k}
    if rename:
        df = df.rename(columns=rename)
    return df


# --- Aggregierte Container für die Pipeline ---
class ERAADataset:
    """Container für alle geladenen ERAA-Output-Daten (kein Pydantic wegen DataFrame)."""

    def __init__(
        self,
        adequacy: pd.DataFrame | None = None,
        dispatch: pd.DataFrame | None = None,
        net_position: pd.DataFrame | None = None,
        prices: pd.DataFrame | None = None,
        storage: pd.DataFrame | None = None,
    ):
        self.adequacy = adequacy
        self.dispatch = dispatch
        self.net_position = net_position
        self.prices = prices
        self.storage = storage
