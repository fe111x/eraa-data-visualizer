"""
Plotly-Visualisierungen für ERAA-Daten.

Erzeugt Boxplots, Heatmaps und Zeitreihen; speichert alle Plots als HTML.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .config import Config


def _fig_defaults(fig: go.Figure, config: Config) -> None:
    w = config.visualization.figure_width
    h = config.visualization.figure_height
    fig.update_layout(
        template=config.visualization.template,
        width=w,
        height=h,
        font=dict(size=12),
        margin=dict(b=80, t=60, l=80, r=40),
    )


def _write_html(fig: go.Figure, path: Path, config: Config) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(
        str(path),
        config=dict(displayModeBar=True, responsive=True),
        include_plotlyjs=config.visualization.html.include_plotlyjs,
    )


# --- Adequacy ---


def plot_adequacy_lole_boxplot(
    df: pd.DataFrame,
    config: Config,
    output_path: Path | None = None,
) -> go.Figure:
    """LOLE pro Study Zone und Target Year als Boxplot (über climate_year × sample)."""
    if df.empty or "lole" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No adequacy data (lole) available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        if output_path:
            _write_html(fig, output_path, config)
        return fig

    # Eine Zeile pro Zone/Jahr/Klimajahr/Sample → Box pro Zone und Target Year
    fig = px.box(
        df,
        x="study_zone",
        y="lole",
        color="target_year",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="LOLE (Loss of Load Expectation) by Study Zone and Target Year",
        labels={"lole": "LOLE [h/year]", "study_zone": "Study Zone"},
    )
    fig.update_xaxes(tickangle=-45)
    _fig_defaults(fig, config)
    if output_path:
        _write_html(fig, output_path, config)
    return fig


def plot_adequacy_ens_boxplot(
    df: pd.DataFrame,
    config: Config,
    output_path: Path | None = None,
) -> go.Figure:
    """ENS (Energy Not Served) pro Zone und Target Year als Boxplot."""
    if df.empty or "ens" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No adequacy data (ens) available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        if output_path:
            _write_html(fig, output_path, config)
        return fig

    fig = px.box(
        df,
        x="study_zone",
        y="ens",
        color="target_year",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="ENS (Energy Not Served) by Study Zone and Target Year",
        labels={"ens": "ENS [GWh]", "study_zone": "Study Zone"},
    )
    fig.update_xaxes(tickangle=-45)
    _fig_defaults(fig, config)
    if output_path:
        _write_html(fig, output_path, config)
    return fig


def plot_adequacy_lole_heatmap(
    df: pd.DataFrame,
    config: Config,
    output_path: Path | None = None,
) -> go.Figure:
    """Heatmap: LOLE (Mittel über Samples) pro Zone × Target Year."""
    if df.empty or "lole" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No adequacy data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        if output_path:
            _write_html(fig, output_path, config)
        return fig

    agg = df.groupby(["study_zone", "target_year"], as_index=False)["lole"].mean()
    pivot = agg.pivot(index="study_zone", columns="target_year", values="lole")
    pivot = pivot.fillna(0)

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=[str(c) for c in pivot.columns],
            y=pivot.index.tolist(),
            colorscale="Reds",
            colorbar=dict(title="LOLE [h/year]"),
        )
    )
    fig.update_layout(
        title="LOLE (average over samples) by Study Zone and Target Year",
        xaxis_title="Target Year",
        yaxis_title="Study Zone",
        template=config.visualization.template,
        width=config.visualization.figure_width,
        height=max(400, len(pivot) * 18),
    )
    if output_path:
        _write_html(fig, output_path, config)
    return fig


# --- Dispatch (Generation) ---


def plot_dispatch_timeseries(
    df: pd.DataFrame,
    config: Config,
    study_zone: str | None = None,
    target_year: int | None = None,
    output_path: Path | None = None,
) -> go.Figure:
    """Zeitreihe: Erzeugung pro Technologie (aggregiert über Samples/Klimajahre oder gefiltert)."""
    if df.empty or "generation_mw" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No dispatch data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        if output_path:
            _write_html(fig, output_path, config)
        return fig

    work = df.copy()
    if study_zone:
        work = work[work["study_zone"] == study_zone]
    if target_year is not None:
        work = work[work["target_year"] == target_year]

    # Aggregation über climate_year und sample_id → Mittel
    group_cols = ["datetime", "technology"]
    if "study_zone" in work.columns and work["study_zone"].nunique() > 1:
        group_cols.insert(0, "study_zone")
    agg = work.groupby(group_cols, as_index=False)["generation_mw"].mean()

    if "datetime" in agg.columns:
        try:
            agg["datetime"] = pd.to_datetime(agg["datetime"])
        except Exception:
            pass
        x = agg["datetime"]
    else:
        x = agg.index

    fig = px.line(
        agg,
        x="datetime",
        y="generation_mw",
        color="technology",
        title=f"Generation by Technology (mean over samples) — {study_zone or 'All zones'} — TY {target_year or 'All'}",
        labels={"generation_mw": "Generation [MW]", "datetime": "Time"},
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    _fig_defaults(fig, config)
    if output_path:
        _write_html(fig, output_path, config)
    return fig


def plot_dispatch_heatmap(
    df: pd.DataFrame,
    config: Config,
    study_zone: str,
    target_year: int,
    output_path: Path | None = None,
) -> go.Figure:
    """Heatmap: Generation (MW) Technologie × Zeit (downsampled wenn nötig)."""
    if df.empty or "generation_mw" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No dispatch data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        if output_path:
            _write_html(fig, output_path, config)
        return fig

    work = df[(df["study_zone"] == study_zone) & (df["target_year"] == target_year)].copy()
    work = work.groupby(["technology", "datetime"], as_index=False)["generation_mw"].mean()

    max_ts = config.visualization.heatmap_max_timesteps
    if work["datetime"].nunique() > max_ts:
        work["datetime"] = pd.to_datetime(work["datetime"], errors="coerce")
        if work["datetime"].isna().all():
            work = work.iloc[: max_ts * work["technology"].nunique()]
        else:
            work = work.sort_values("datetime").groupby("technology").apply(
                lambda g: g.iloc[:: max(1, len(g) // max_ts)]
            ).reset_index(drop=True)

    pivot = work.pivot(index="technology", columns="datetime", values="generation_mw").fillna(0)
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=[str(x) for x in pivot.columns],
            y=pivot.index.tolist(),
            colorscale="Blues",
            colorbar=dict(title="Generation [MW]"),
        )
    )
    fig.update_layout(
        title=f"Generation by Technology — {study_zone} — TY {target_year}",
        xaxis_title="Time",
        yaxis_title="Technology",
        template=config.visualization.template,
        width=config.visualization.figure_width,
        height=max(300, len(pivot) * 24),
    )
    if output_path:
        _write_html(fig, output_path, config)
    return fig


# --- Net Position ---


def plot_net_position_timeseries(
    df: pd.DataFrame,
    config: Config,
    target_year: int | None = None,
    output_path: Path | None = None,
) -> go.Figure:
    """Zeitreihe Net Position (Mittel über Samples) pro Study Zone."""
    if df.empty or "net_position_mw" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No net position data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        if output_path:
            _write_html(fig, output_path, config)
        return fig

    work = df.copy()
    if target_year is not None:
        work = work[work["target_year"] == target_year]
    agg = work.groupby(["datetime", "study_zone"], as_index=False)["net_position_mw"].mean()
    try:
        agg["datetime"] = pd.to_datetime(agg["datetime"])
    except Exception:
        pass

    fig = px.line(
        agg,
        x="datetime",
        y="net_position_mw",
        color="study_zone",
        title=f"Net Position by Market Area (mean over samples) — TY {target_year or 'All'}",
        labels={"net_position_mw": "Net Position [MW]", "datetime": "Time"},
    )
    _fig_defaults(fig, config)
    if output_path:
        _write_html(fig, output_path, config)
    return fig


def plot_net_position_heatmap(
    df: pd.DataFrame,
    config: Config,
    target_year: int,
    output_path: Path | None = None,
) -> go.Figure:
    """Heatmap: Net Position Zone × Zeit (Mittel über Samples)."""
    if df.empty or "net_position_mw" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No net position data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        if output_path:
            _write_html(fig, output_path, config)
        return fig

    work = df[df["target_year"] == target_year].copy()
    agg = work.groupby(["study_zone", "datetime"], as_index=False)["net_position_mw"].mean()
    max_ts = config.visualization.heatmap_max_timesteps
    if agg["datetime"].nunique() > max_ts:
        agg = agg.sort_values("datetime").groupby("study_zone").apply(
            lambda g: g.iloc[:: max(1, len(g) // max_ts)]
        ).reset_index(drop=True)
    pivot = agg.pivot(index="study_zone", columns="datetime", values="net_position_mw").fillna(0)
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=[str(x) for x in pivot.columns],
            y=pivot.index.tolist(),
            colorscale="RdBu",
            zmid=0,
            colorbar=dict(title="Net Position [MW]"),
        )
    )
    fig.update_layout(
        title=f"Net Position by Market Area — TY {target_year}",
        xaxis_title="Time",
        yaxis_title="Study Zone",
        template=config.visualization.template,
        width=config.visualization.figure_width,
        height=max(400, len(pivot) * 18),
    )
    if output_path:
        _write_html(fig, output_path, config)
    return fig


# --- Prices ---


def plot_prices_timeseries(
    df: pd.DataFrame,
    config: Config,
    study_zone: str | None = None,
    target_year: int | None = None,
    output_path: Path | None = None,
) -> go.Figure:
    """Zeitreihe Preise [€/MWh] (Mittel über Samples)."""
    if df.empty or "price_eur_mwh" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No price data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        if output_path:
            _write_html(fig, output_path, config)
        return fig

    work = df.copy()
    if study_zone:
        work = work[work["study_zone"] == study_zone]
    if target_year is not None:
        work = work[work["target_year"] == target_year]
    agg = work.groupby(["datetime", "study_zone"], as_index=False)["price_eur_mwh"].mean()
    try:
        agg["datetime"] = pd.to_datetime(agg["datetime"])
    except Exception:
        pass

    fig = px.line(
        agg,
        x="datetime",
        y="price_eur_mwh",
        color="study_zone",
        title=f"Electricity Price [€/MWh] (mean over samples) — TY {target_year or 'All'}",
        labels={"price_eur_mwh": "Price [€/MWh]", "datetime": "Time"},
    )
    _fig_defaults(fig, config)
    if output_path:
        _write_html(fig, output_path, config)
    return fig


def plot_prices_boxplot(
    df: pd.DataFrame,
    config: Config,
    target_year: int | None = None,
    output_path: Path | None = None,
) -> go.Figure:
    """Boxplot Preise pro Zone und ggf. Target Year."""
    if df.empty or "price_eur_mwh" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No price data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        if output_path:
            _write_html(fig, output_path, config)
        return fig

    work = df.copy()
    if target_year is not None:
        work = work[work["target_year"] == target_year]
    fig = px.box(
        work,
        x="study_zone",
        y="price_eur_mwh",
        color="target_year" if "target_year" in work.columns and work["target_year"].nunique() > 1 else None,
        title=f"Price Distribution by Zone — TY {target_year or 'All'}",
        labels={"price_eur_mwh": "Price [€/MWh]", "study_zone": "Study Zone"},
    )
    fig.update_xaxes(tickangle=-45)
    _fig_defaults(fig, config)
    if output_path:
        _write_html(fig, output_path, config)
    return fig


# --- Storage ---


def plot_storage_level_timeseries(
    df: pd.DataFrame,
    config: Config,
    study_zone: str | None = None,
    storage_type: str | None = None,
    target_year: int | None = None,
    output_path: Path | None = None,
) -> go.Figure:
    """Zeitreihe Speicherfüllstand (level_pct oder level_mwh)."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No storage data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        if output_path:
            _write_html(fig, output_path, config)
        return fig

    y_col = "level_pct" if "level_pct" in df.columns else "level_mwh"
    if y_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="No level_pct/level_mwh in storage data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        if output_path:
            _write_html(fig, output_path, config)
        return fig

    work = df.copy()
    if study_zone:
        work = work[work["study_zone"] == study_zone]
    if storage_type:
        work = work[work["storage_type"] == storage_type]
    if target_year is not None:
        work = work[work["target_year"] == target_year]
    agg = work.groupby(["datetime", "study_zone", "storage_type"], as_index=False)[y_col].mean()
    try:
        agg["datetime"] = pd.to_datetime(agg["datetime"])
    except Exception:
        pass
    agg["series"] = agg["study_zone"] + " — " + agg["storage_type"]

    fig = px.line(
        agg,
        x="datetime",
        y=y_col,
        color="series",
        title=f"Storage Level ({y_col}) — TY {target_year or 'All'}",
        labels={y_col: "Level [%]" if y_col == "level_pct" else "Level [MWh]", "datetime": "Time"},
    )
    _fig_defaults(fig, config)
    if output_path:
        _write_html(fig, output_path, config)
    return fig


def run_all_plots(dataset: "ERAADataset", config: Config) -> list[Path]:
    """Führt alle verfügbaren Plots aus und gibt die gespeicherten HTML-Pfade zurück."""
    written: list[Path] = []

    if dataset.adequacy is not None and not dataset.adequacy.empty:
        p = config.output_path("adequacy", "adequacy_lole_boxplot.html")
        plot_adequacy_lole_boxplot(dataset.adequacy, config, p)
        written.append(p)
        p = config.output_path("adequacy", "adequacy_ens_boxplot.html")
        plot_adequacy_ens_boxplot(dataset.adequacy, config, p)
        written.append(p)
        p = config.output_path("adequacy", "adequacy_lole_heatmap.html")
        plot_adequacy_lole_heatmap(dataset.adequacy, config, p)
        written.append(p)

    if dataset.dispatch is not None and not dataset.dispatch.empty:
        p = config.output_path("dispatch", "dispatch_timeseries_mean.html")
        plot_dispatch_timeseries(dataset.dispatch, config, output_path=p)
        written.append(p)
        zones = dataset.dispatch["study_zone"].unique()[:3]
        years = dataset.dispatch["target_year"].unique()
        for sz in zones:
            for ty in years:
                p = config.output_path("dispatch", f"dispatch_heatmap_{sz}_TY{ty}.html")
                plot_dispatch_heatmap(dataset.dispatch, config, sz, int(ty), p)
                written.append(p)

    if dataset.net_position is not None and not dataset.net_position.empty:
        p = config.output_path("net_position", "net_position_timeseries.html")
        plot_net_position_timeseries(dataset.net_position, config, output_path=p)
        written.append(p)
        for ty in dataset.net_position["target_year"].unique():
            p = config.output_path("net_position", f"net_position_heatmap_TY{ty}.html")
            plot_net_position_heatmap(dataset.net_position, config, int(ty), p)
            written.append(p)

    if dataset.prices is not None and not dataset.prices.empty:
        p = config.output_path("prices", "prices_timeseries.html")
        plot_prices_timeseries(dataset.prices, config, output_path=p)
        written.append(p)
        p = config.output_path("prices", "prices_boxplot.html")
        plot_prices_boxplot(dataset.prices, config, output_path=p)
        written.append(p)

    if dataset.storage is not None and not dataset.storage.empty:
        p = config.output_path("storage", "storage_level_timeseries.html")
        plot_storage_level_timeseries(dataset.storage, config, output_path=p)
        written.append(p)

    return written
