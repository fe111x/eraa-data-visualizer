"""Hauptpipeline: Daten laden → Visualisierungen erzeugen → HTML ausgeben."""

from __future__ import annotations

from pathlib import Path

from .config import Config
from .loaders import load_dataset
from .plots import run_all_plots


def run_pipeline(config_path: str | Path | None = None) -> list[Path]:
    """
    Lädt Konfiguration, lädt alle verfügbaren ERAA-Daten und erzeugt alle Plots als HTML.

    Returns:
        Liste der geschriebenen HTML-Dateipfade.
    """
    config = Config.load(config_path or "config.yaml")
    Path(config.paths.output_dir).mkdir(parents=True, exist_ok=True)
    dataset = load_dataset(config)
    return run_all_plots(dataset, config)


if __name__ == "__main__":
    written = run_pipeline()
    for p in written:
        print("Written:", p)
