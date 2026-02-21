"""Tests für eraa_visualizer.plots – alle Plot-Funktionen liefern eine go.Figure."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pytest


@pytest.fixture
def config():
    from eraa_visualizer.config import Config
    return Config()


def test_plot_adequacy_lole_boxplot(config, df_adequacy):
    from eraa_visualizer.plots import plot_adequacy_lole_boxplot
    fig = plot_adequacy_lole_boxplot(df_adequacy, config)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1


def test_plot_adequacy_lole_boxplot_empty(config):
    from eraa_visualizer.plots import plot_adequacy_lole_boxplot
    fig = plot_adequacy_lole_boxplot(pd.DataFrame(), config)
    assert isinstance(fig, go.Figure)


def test_plot_adequacy_ens_boxplot(config, df_adequacy):
    from eraa_visualizer.plots import plot_adequacy_ens_boxplot
    fig = plot_adequacy_ens_boxplot(df_adequacy, config)
    assert isinstance(fig, go.Figure)


def test_plot_adequacy_lole_heatmap(config, df_adequacy):
    from eraa_visualizer.plots import plot_adequacy_lole_heatmap
    fig = plot_adequacy_lole_heatmap(df_adequacy, config)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1


def test_plot_adequacy_lole_heatmap_hour_month(config, df_adequacy_hour_month):
    from eraa_visualizer.plots import plot_adequacy_lole_heatmap_hour_month
    fig = plot_adequacy_lole_heatmap_hour_month(df_adequacy_hour_month, config)
    assert isinstance(fig, go.Figure)


def test_plot_adequacy_ens_heatmap_hour_month(config, df_adequacy_hour_month):
    from eraa_visualizer.plots import plot_adequacy_ens_heatmap_hour_month
    fig = plot_adequacy_ens_heatmap_hour_month(df_adequacy_hour_month, config)
    assert isinstance(fig, go.Figure)


def test_plot_adequacy_europe_map(config, df_adequacy):
    from eraa_visualizer.plots import plot_adequacy_europe_map
    fig = plot_adequacy_europe_map(df_adequacy, config, metric="lole")
    assert isinstance(fig, go.Figure)
    fig2 = plot_adequacy_europe_map(df_adequacy, config, metric="ens")
    assert isinstance(fig2, go.Figure)


def test_plot_dispatch_timeseries(config, df_dispatch):
    from eraa_visualizer.plots import plot_dispatch_timeseries
    fig = plot_dispatch_timeseries(df_dispatch, config)
    assert isinstance(fig, go.Figure)


def test_plot_dispatch_heatmap(config, df_dispatch):
    from eraa_visualizer.plots import plot_dispatch_heatmap
    fig = plot_dispatch_heatmap(df_dispatch, config, "DE00", 2025)
    assert isinstance(fig, go.Figure)


def test_plot_dispatch_heatmap_hour_month(config, df_dispatch):
    from eraa_visualizer.plots import plot_dispatch_heatmap_hour_month
    fig = plot_dispatch_heatmap_hour_month(df_dispatch, config, "DE00", 2025)
    assert isinstance(fig, go.Figure)


def test_plot_net_position_timeseries(config, df_net_position):
    from eraa_visualizer.plots import plot_net_position_timeseries
    fig = plot_net_position_timeseries(df_net_position, config)
    assert isinstance(fig, go.Figure)


def test_plot_net_position_heatmap(config, df_net_position):
    from eraa_visualizer.plots import plot_net_position_heatmap
    fig = plot_net_position_heatmap(df_net_position, config, 2025)
    assert isinstance(fig, go.Figure)


def test_plot_net_position_heatmap_hour_month(config, df_net_position):
    from eraa_visualizer.plots import plot_net_position_heatmap_hour_month
    fig = plot_net_position_heatmap_hour_month(df_net_position, config, "DE00", 2025)
    assert isinstance(fig, go.Figure)


def test_plot_prices_timeseries(config, df_prices):
    from eraa_visualizer.plots import plot_prices_timeseries
    fig = plot_prices_timeseries(df_prices, config)
    assert isinstance(fig, go.Figure)


def test_plot_prices_boxplot(config, df_prices):
    from eraa_visualizer.plots import plot_prices_boxplot
    fig = plot_prices_boxplot(df_prices, config)
    assert isinstance(fig, go.Figure)


def test_plot_prices_heatmap_hour_month(config, df_prices):
    from eraa_visualizer.plots import plot_prices_heatmap_hour_month
    fig = plot_prices_heatmap_hour_month(df_prices, config, "DE00", 2025)
    assert isinstance(fig, go.Figure)


def test_plot_storage_level_timeseries(config, df_storage):
    from eraa_visualizer.plots import plot_storage_level_timeseries
    fig = plot_storage_level_timeseries(df_storage, config)
    assert isinstance(fig, go.Figure)


def test_run_all_plots(config, df_adequacy, df_dispatch, df_net_position, df_prices, df_storage, df_adequacy_hour_month, tmp_path):
    from eraa_visualizer.plots import run_all_plots
    from eraa_visualizer.models import ERAADataset
    from eraa_visualizer.config import Config, PathsConfig
    cfg = config.model_copy(update={"paths": config.paths.model_copy(update={"output_dir": str(tmp_path)})})
    dataset = ERAADataset(
        adequacy=df_adequacy,
        adequacy_hour_month=df_adequacy_hour_month,
        dispatch=df_dispatch,
        net_position=df_net_position,
        prices=df_prices,
        storage=df_storage,
    )
    written = run_all_plots(dataset, cfg)
    assert isinstance(written, list)
    assert len(written) >= 1
    for p in written:
        assert hasattr(p, "exists")
        assert p.exists()
