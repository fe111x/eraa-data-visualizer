"""CLI für ERAA Data Visualizer."""

from __future__ import annotations

from pathlib import Path

import click

from .pipeline import run_pipeline


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(path_type=Path, exists=True),
    default="config.yaml",
    help="Pfad zur config.yaml",
)
@click.option(
    "--list-only",
    is_flag=True,
    help="Nur auflisten, welche Daten/Plots erzeugt würden (ohne zu schreiben).",
)
def main(config: Path, list_only: bool) -> None:
    """ERAA Data Visualizer – Visualisierungspipeline für ERAA-Modelloutputs."""
    if list_only:
        from .config import Config
        from .loaders import load_dataset

        cfg = Config.load(config)
        dataset = load_dataset(cfg)
        click.echo("Geladene Daten:")
        click.echo(f"  Adequacy:      {dataset.adequacy is not None and not dataset.adequacy.empty}")
        click.echo(f"  Dispatch:      {dataset.dispatch is not None and not dataset.dispatch.empty}")
        click.echo(f"  Net Position:  {dataset.net_position is not None and not dataset.net_position.empty}")
        click.echo(f"  Prices:        {dataset.prices is not None and not dataset.prices.empty}")
        click.echo(f"  Storage:       {dataset.storage is not None and not dataset.storage.empty}")
        click.echo("Run without --list-only to generate HTML plots.")
        return

    click.echo("Running ERAA visualization pipeline...")
    written = run_pipeline(config)
    click.echo(f"Done. Written {len(written)} HTML file(s) to {Path(written[0]).parent if written else 'N/A'}.")
    for p in written:
        click.echo(f"  {p}")


if __name__ == "__main__":
    main()
