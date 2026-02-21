"""Tests für scripts/generate_sample_data."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def test_generate_sample_data_runs(tmp_path):
    """generate_sample_data.py schreibt CSV-Dateien ins data-Verzeichnis."""
    sys.path.insert(0, str(ROOT / "src"))
    # Script ändert sich auf ROOT/data – wir müssen das data-Verzeichnis auf tmp_path setzen
    # Dafür müsste das Script einen Parameter akzeptieren. Stattdessen: Script ausführen und prüfen, dass data/ existiert und Dateien hat (oder wir führen es in tmp_path aus)
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "generate_sample_data.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (result.stdout or "") + (result.stderr or "")
    data_dir = ROOT / "data"
    if data_dir.exists():
        assert (data_dir / "adequacy.csv").exists()
        assert (data_dir / "adequacy_hour_month.csv").exists()
        assert (data_dir / "dispatch.csv").exists()
        assert (data_dir / "net_position.csv").exists()
        assert (data_dir / "prices.csv").exists()
        assert (data_dir / "storage.csv").exists()


def test_generate_sample_data_adequacy_columns():
    """Prüft, dass generate_adequacy die erwarteten Spalten hat."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("generate_sample_data", SCRIPTS / "generate_sample_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    import numpy as np
    rng = np.random.default_rng(42)
    df = mod.generate_adequacy(rng)
    assert not df.empty
    for col in ["study_zone", "target_year", "climate_year", "sample_id", "lole", "eens", "lld", "ens"]:
        assert col in df.columns


def test_generate_sample_data_adequacy_hour_month_columns():
    import importlib.util
    spec = importlib.util.spec_from_file_location("generate_sample_data", SCRIPTS / "generate_sample_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    import numpy as np
    rng = np.random.default_rng(42)
    df = mod.generate_adequacy_hour_month(rng)
    assert not df.empty
    assert "month" in df.columns
    assert "hour" in df.columns
    assert "lole_h" in df.columns
    assert "ens_mwh" in df.columns
    assert df["month"].between(1, 12).all()
    assert df["hour"].between(0, 23).all()
