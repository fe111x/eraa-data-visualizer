"""
ERAA Data Visualizer – Streamlit Dashboard.

Zeigt Adequacy (LOLE, ENS), Dispatch, Net Position, Preise und Speicher
mit Filtern; Heatmaps Stunde×Monat; Europakarte; Seiten Datenmodell & ERAA-Prozess.
Start: streamlit run app/dashboard.py (aus Projektroot).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas as pd
import streamlit as st

from eraa_visualizer.config import Config
from eraa_visualizer.loaders import load_dataset
from eraa_visualizer.plots import (
    plot_adequacy_ens_boxplot,
    plot_adequacy_ens_heatmap_hour_month,
    plot_adequacy_europe_map,
    plot_adequacy_lole_boxplot,
    plot_adequacy_lole_heatmap,
    plot_adequacy_lole_heatmap_hour_month,
    plot_dispatch_heatmap,
    plot_dispatch_heatmap_hour_month,
    plot_dispatch_timeseries,
    plot_net_position_heatmap,
    plot_net_position_heatmap_hour_month,
    plot_net_position_timeseries,
    plot_prices_boxplot,
    plot_prices_heatmap_hour_month,
    plot_prices_timeseries,
    plot_storage_level_timeseries,
)


def _filter_df(
    df: pd.DataFrame | None,
    *,
    target_years: list[int] | None = None,
    study_zones: list[str] | None = None,
) -> pd.DataFrame | None:
    if df is None or df.empty:
        return df
    out = df.copy()
    if target_years:
        if "target_year" in out.columns:
            out = out[out["target_year"].isin(target_years)]
    if study_zones:
        if "study_zone" in out.columns:
            out = out[out["study_zone"].isin(study_zones)]
    return out if not out.empty else None


@st.cache_data
def _load_config_and_data():
    config = Config.load(ROOT / "config.yaml")
    dataset = load_dataset(config)
    return config, dataset


def _render_header():
    st.markdown(
        """
        <style>
        .eraa-header {
            background: linear-gradient(90deg, #003366 0%, #00509e 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            font-family: sans-serif;
        }
        .eraa-header h1 { margin: 0; font-size: 1.6rem; }
        .eraa-header p { margin: 0.3rem 0 0 0; opacity: 0.9; font-size: 0.95rem; }
        </style>
        <div class="eraa-header">
            <h1>⚡ ERAA Data Visualizer</h1>
            <p>European Resource Adequacy Assessment – Adequacy, Dispatch, Net Position, Preise & Speicher</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _sidebar_filters(config: Config, dataset):
    target_years_available = []
    study_zones_available = []
    for df in [dataset.adequacy, dataset.dispatch, dataset.net_position, dataset.prices, dataset.storage]:
        if df is not None and not df.empty:
            if "target_year" in df.columns:
                target_years_available.extend(df["target_year"].unique().tolist())
            if "study_zone" in df.columns:
                study_zones_available.extend(df["study_zone"].unique().tolist())
    target_years_available = sorted(set(target_years_available)) or config.dimensions.target_years
    study_zones_available = sorted(set(study_zones_available))

    filter_target = st.sidebar.multiselect(
        "Target Year (Zieljahr)",
        options=target_years_available,
        default=target_years_available[:2] if len(target_years_available) > 2 else target_years_available,
        help="Mehrere Jahre wählbar.",
    )
    filter_zones = st.sidebar.multiselect(
        "Study Zone (Marktgebiet)",
        options=study_zones_available,
        default=study_zones_available[:5] if len(study_zones_available) > 5 else study_zones_available,
        help="Leer = alle.",
    )
    filter_ty = filter_target if len(filter_target) > 0 else None
    filter_z = filter_zones if len(filter_zones) > 0 else None
    return filter_ty, filter_z


def page_visualizations(config, adeq, adeq_hm, disp, netpos, prices, storage):
    tab_adequacy, tab_dispatch, tab_netpos, tab_prices, tab_storage = st.tabs([
        "Adequacy (LOLE & ENS)",
        "Dispatch (Erzeugung)",
        "Net Position",
        "Preise",
        "Speicher",
    ])

    with tab_adequacy:
        if adeq is not None and not adeq.empty:
            st.subheader("Loss of Load Expectation (LOLE) und Energy Not Served (ENS)")
            c1, c2 = st.columns(2)
            with c1:
                fig = plot_adequacy_lole_boxplot(adeq, config)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig = plot_adequacy_ens_boxplot(adeq, config)
                st.plotly_chart(fig, use_container_width=True)
            st.subheader("LOLE – Heatmap Zone × Zieljahr")
            fig = plot_adequacy_lole_heatmap(adeq, config)
            st.plotly_chart(fig, use_container_width=True)
            # Stunde × Monat (LOLE / ENS)
            if adeq_hm is not None and not adeq_hm.empty:
                st.subheader("LOLE und ENS – Stunde (24h) × Monat (12)")
                zone_hm = st.selectbox("Zone (Stunde×Monat)", options=["Alle"] + sorted(adeq_hm["study_zone"].unique().tolist()), key="adeq_hm_zone")
                ty_hm = st.selectbox("Zieljahr (Stunde×Monat)", options=[None] + sorted(adeq_hm["target_year"].unique().tolist()), key="adeq_hm_ty", format_func=lambda x: "Alle" if x is None else str(x))
                c1, c2 = st.columns(2)
                with c1:
                    fig = plot_adequacy_lole_heatmap_hour_month(adeq_hm, config, study_zone=None if zone_hm == "Alle" else zone_hm, target_year=ty_hm)
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    fig = plot_adequacy_ens_heatmap_hour_month(adeq_hm, config, study_zone=None if zone_hm == "Alle" else zone_hm, target_year=ty_hm)
                    st.plotly_chart(fig, use_container_width=True)
            st.subheader("Europakarte – Jahres-LOLE und -ENS pro Land")
            map_ty = st.selectbox("Zieljahr (Karte)", options=[None] + sorted(adeq["target_year"].unique().tolist()), key="map_ty", format_func=lambda x: "Alle" if x is None else str(x))
            c1, c2 = st.columns(2)
            with c1:
                fig = plot_adequacy_europe_map(adeq, config, metric="lole", target_year=map_ty)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig = plot_adequacy_europe_map(adeq, config, metric="ens", target_year=map_ty)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Keine Adequacy-Daten. Bitte Beispieldaten mit `python3.11 scripts/generate_sample_data.py` erzeugen.")

    with tab_dispatch:
        if disp is not None and not disp.empty:
            st.subheader("Erzeugung nach Technologie (Zeitreihe)")
            disp_zone = st.selectbox("Study Zone", options=["Alle"] + sorted(disp["study_zone"].unique().tolist()), key="disp_zone")
            disp_ty = st.selectbox("Target Year", options=[None] + sorted(disp["target_year"].unique().tolist()), key="disp_ty", format_func=lambda x: "Alle" if x is None else str(x))
            fig = plot_dispatch_timeseries(disp, config, study_zone=None if disp_zone == "Alle" else disp_zone, target_year=disp_ty)
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("Erzeugung – Heatmap Technologie × Zeit")
            hz = st.selectbox("Zone (Heatmap)", sorted(disp["study_zone"].unique().tolist()), key="heat_zone")
            hy = st.selectbox("Zieljahr (Heatmap)", sorted(disp["target_year"].unique().tolist()), key="heat_year")
            fig = plot_dispatch_heatmap(disp, config, hz, int(hy))
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("Erzeugung – Stunde × Monat")
            tech_hm = st.selectbox("Technologie (Stunde×Monat)", options=["Alle"] + sorted(disp["technology"].unique().tolist()), key="disp_tech_hm")
            fig = plot_dispatch_heatmap_hour_month(disp, config, hz, int(hy), technology=None if tech_hm == "Alle" else tech_hm)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Keine Dispatch-Daten.")

    with tab_netpos:
        if netpos is not None and not netpos.empty:
            st.subheader("Net Position (Zeitreihe)")
            np_ty = st.selectbox("Target Year", options=[None] + sorted(netpos["target_year"].unique().tolist()), key="np_ty", format_func=lambda x: "Alle" if x is None else str(x))
            fig = plot_net_position_timeseries(netpos, config, target_year=np_ty)
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("Net Position – Heatmap Zone × Zeit")
            for ty in sorted(netpos["target_year"].unique().tolist()):
                fig = plot_net_position_heatmap(netpos, config, int(ty))
                st.plotly_chart(fig, use_container_width=True)
            st.subheader("Net Position – Stunde × Monat")
            np_zone = st.selectbox("Zone (Stunde×Monat)", sorted(netpos["study_zone"].unique().tolist()), key="np_zone_hm")
            np_ty_hm = st.selectbox("Zieljahr (Stunde×Monat)", sorted(netpos["target_year"].unique().tolist()), key="np_ty_hm")
            fig = plot_net_position_heatmap_hour_month(netpos, config, np_zone, int(np_ty_hm))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Keine Net-Position-Daten.")

    with tab_prices:
        if prices is not None and not prices.empty:
            st.subheader("Strompreis [€/MWh] – Zeitreihe")
            fig = plot_prices_timeseries(prices, config)
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("Preisverteilung (Boxplot)")
            fig = plot_prices_boxplot(prices, config)
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("Preis – Stunde × Monat")
            pr_zone = st.selectbox("Zone (Stunde×Monat)", sorted(prices["study_zone"].unique().tolist()), key="pr_zone_hm")
            pr_ty = st.selectbox("Zieljahr (Stunde×Monat)", sorted(prices["target_year"].unique().tolist()), key="pr_ty_hm")
            fig = plot_prices_heatmap_hour_month(prices, config, pr_zone, int(pr_ty))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Keine Preisdaten.")

    with tab_storage:
        if storage is not None and not storage.empty:
            st.subheader("Speicherfüllstand")
            fig = plot_storage_level_timeseries(storage, config)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Keine Speicherdaten.")


def page_europe_map(config, adeq):
    st.subheader("Europakarte – LOLE und ENS pro Land")
    if adeq is None or adeq.empty:
        st.info("Keine Adequacy-Daten für die Karte.")
        return
    map_ty = st.selectbox("Zieljahr", options=[None] + sorted(adeq["target_year"].unique().tolist()), key="eu_map_ty", format_func=lambda x: "Alle" if x is None else str(x))
    c1, c2 = st.columns(2)
    with c1:
        fig = plot_adequacy_europe_map(adeq, config, metric="lole", target_year=map_ty)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = plot_adequacy_europe_map(adeq, config, metric="ens", target_year=map_ty)
        st.plotly_chart(fig, use_container_width=True)


def page_data_model():
    st.subheader("Datenmodell – Tabellen und Ausprägungen")
    st.markdown("""
    Das ERAA-Output-Datenmodell besteht aus **fünf Kern-Tabellen**. Jede Tabelle hat feste Dimensionen und Kennzahlen.
    """)
    data = [
        ("**Adequacy**", "study_zone, target_year, scenario, climate_year, sample_id", "lole, eens, lld, ens, p50_lld, p95_lld, p50_ens, p95_ens", "Eine Zeile pro Zone, Zieljahr, Klimajahr und Sample (z. B. 36×10 Läufe)."),
        ("**Adequacy (Stunde×Monat)**", "study_zone, target_year, climate_year, sample_id, month, hour", "lole_h, ens_mwh", "LOLE/ENS auf 24 Stunden × 12 Monate verteilt (für Heatmaps)."),
        ("**Dispatch**", "study_zone, target_year, technology, datetime, climate_year, sample_id", "generation_mw, load_mw", "Erzeugung und Ladung (z. B. Pumpspeicher) pro Technologie und Zeitschritt."),
        ("**Net Position**", "study_zone, target_year, datetime, climate_year, sample_id", "net_position_mw", "Netto-Import/Export pro Marktgebiet und Zeitschritt."),
        ("**Prices**", "study_zone, target_year, datetime, climate_year, sample_id", "price_eur_mwh", "Strompreis [€/MWh] pro Zone und Zeitschritt."),
        ("**Storage**", "study_zone, target_year, storage_type, datetime, climate_year, sample_id", "level_pct, level_mwh", "Speicherfüllstand pro Typ und Zeitschritt."),
    ]
    for name, dims, metrics, desc in data:
        with st.expander(name, expanded=True):
            st.markdown(f"**Dimensionen:** `{dims}`  ")
            st.markdown(f"**Kennzahlen:** `{metrics}`  ")
            st.caption(desc)
    st.markdown("---")
    st.caption("Spaltennamen können in `config.yaml` unter `schema` angepasst werden.")


def page_eraa_process():
    st.subheader("Zum ERAA-Prozess")
    path = ROOT / "docs" / "ERAA_BACKGROUND.md"
    if path.exists():
        st.markdown(path.read_text(encoding="utf-8"))
    else:
        st.markdown("""
        **European Resource Adequacy Assessment (ERAA)** ist die paneuropäische Bewertung der Versorgungsadequacy durch ENTSO-E (bis 10 Jahre Vorlauf).
        Es nutzt probabilistische Methoden über viele **Klimajahre** und **Outage-Samples** (typisch 36×10).  
        Kennzahlen: **LOLE** (Loss of Load Expectation, h/Jahr), **ENS** (Energy Not Served, GWh).  
        [ENTSO-E ERAA](https://www.entsoe.eu/eraa/)
        """)


def main() -> None:
    st.set_page_config(
        page_title="ERAA Data Visualizer",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _render_header()
    config, dataset = _load_config_and_data()
    filter_ty, filter_z = _sidebar_filters(config, dataset)

    adeq = _filter_df(dataset.adequacy, target_years=filter_ty, study_zones=filter_z)
    adeq_hm = _filter_df(dataset.adequacy_hour_month, target_years=filter_ty, study_zones=filter_z)
    disp = _filter_df(dataset.dispatch, target_years=filter_ty, study_zones=filter_z)
    netpos = _filter_df(dataset.net_position, target_years=filter_ty, study_zones=filter_z)
    prices = _filter_df(dataset.prices, target_years=filter_ty, study_zones=filter_z)
    storage = _filter_df(dataset.storage, target_years=filter_ty, study_zones=filter_z)

    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Seite",
        ["Visualisierungen", "Europakarte", "Datenmodell", "ERAA-Prozess"],
        label_visibility="collapsed",
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Daten: Ordner `data/`. Beispieldaten: `python3.11 scripts/generate_sample_data.py`")
    st.sidebar.markdown("[ENTSO-E ERAA](https://www.entsoe.eu/eraa/)")

    if page == "Visualisierungen":
        page_visualizations(config, adeq, adeq_hm, disp, netpos, prices, storage)
    elif page == "Europakarte":
        page_europe_map(config, adeq)
    elif page == "Datenmodell":
        page_data_model()
    else:
        page_eraa_process()


if __name__ == "__main__":
    main()
