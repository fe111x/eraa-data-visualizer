# ERAA Data Visualizer

Visualisierungspipeline für **European Resource Adequacy Assessment (ERAA)** Modelloutputs. Erzeugt Plotly-Plots (Boxplots, Heatmaps, Zeitreihen) für Adequacy (LOLE, ENS), Economic Dispatch, Net Position, Preise und Speicherfüllstände – alle Ausgaben als HTML.

## Hintergrund: ERAA

Das **European Resource Adequacy Assessment** ist die paneuropäische Bewertung der Versorgungsadequacy durch ENTSO-E (bis 10 Jahre Vorlauf). Es nutzt probabilistische Methoden über viele **Klimajahre** und **Outage-Samples**, um LOLE (Loss of Load Expectation) und ENS (Energy Not Served) pro Study Zone zu berechnen. Typische Modelloutputs umfassen:

- **Adequacy**: LOLE, EENS, LLD, ENS (und Perzentile P50, P95) pro Zone, Zieljahr, Klimajahr, Sample
- **Economic Dispatch**: Erzeugung und Ladung (z. B. Pumpspeicher, Batterien) nach **PEMMDB**-Technologietypen
- **Net Position**: Netto-Import/Export pro Marktgebiet
- **Preise**: Strompreise [€/MWh]
- **Speicher**: Füllstände (level_pct / level_mwh) pro Speichertyp

Die Pipeline baut auf einem **generischen Datenmodell** auf, das genau diese Output-Strukturen abbildet (inkl. Dimensionen wie `climate_year`, `sample_id`). In der Konfiguration sind typischerweise **36 Klimajahre × 10 Samples** pro Zieljahr hinterlegt.

## Installation

**Empfohlen: UV** (Python ≥3.11)

```bash
# UV installieren: https://docs.astral.sh/uv/getting-started/installation/
uv sync
```

**Alternative: pip**

```bash
pip install -r requirements.txt
# Paket für CLI lokal nutzbar machen:
export PYTHONPATH=src
python -m eraa_visualizer.cli --help
```

Abhängigkeiten werden aus `pyproject.toml` bzw. `requirements.txt` bezogen.

## Konfiguration

In **`config.yaml`** können Sie festlegen:

- **paths**: `data_dir` (Eingabedaten), `output_dir` (HTML-Ausgabe), Unterordner pro Kategorie
- **dimensions**: `n_climate_years`, `n_samples_per_climate_year`, `target_years`
- **technology**: Listen für Generation- und Storage-Typen (PEMMDB)
- **visualization**: Plotly-Template, Größen, HTML-Optionen, Heatmap-Downsampling
- **schema**: Spaltennamen-Mapping pro Kategorie (adequacy, dispatch, net_position, prices, storage)

So können unterschiedliche Modellformate (andere Spaltennamen) angepasst werden.

## Datenformat (Eingabe)

Erwartet werden CSV- oder Parquet-Dateien unter `data_dir` mit den in `config.yaml` unter `schema` definierten Spalten (oder den Standard-Namen). Beispiele:

| Kategorie     | Dateiname (alternativ)   | Wichtige Spalten |
|---------------|---------------------------|------------------|
| Adequacy      | `adequacy.csv` / `.parquet` | study_zone, target_year, climate_year, sample_id, lole, eens, lld, ens |
| Dispatch      | `dispatch.csv` / `generation.csv` | study_zone, target_year, technology, datetime, climate_year, sample_id, generation_mw, load_mw |
| Net Position  | `net_position.csv`        | study_zone, target_year, datetime, climate_year, sample_id, net_position_mw |
| Prices        | `prices.csv`              | study_zone, target_year, datetime, climate_year, sample_id, price_eur_mwh |
| Storage       | `storage.csv`             | study_zone, target_year, storage_type, datetime, climate_year, sample_id, level_pct, level_mwh |

Fehlende Kategorien werden übersprungen; für jede vorhandene Kategorie werden die zugehörigen Plots erzeugt.

## Dashboard (Streamlit)

Alle Visualisierungen gibt es auch als **interaktives Web-Dashboard** mit Filtern (Zieljahr, Study Zone), angelehnt an das [offizielle ERAA-Dashboard](https://www.entsoe.eu/eraa/2024/modelling-data) von ENTSO-E.

**Starten:** Aus Projektroot `uv run streamlit run app/dashboard.py` ausführen, dann im Browser **http://localhost:8501** öffnen.

Ausführliche Anleitung: **[README_DASHBOARD.md](README_DASHBOARD.md)** (lokaler Start, Browser, Beispieldaten).

---

## Nutzung

### Pipeline ausführen (alle Plots)

```bash
uv run eraa-viz
# oder mit expliziter Config
uv run eraa-viz --config config.yaml
```

### Nur prüfen, welche Daten geladen würden

```bash
uv run eraa-viz --list-only
```

### Beispieldaten erzeugen und visualisieren

```bash
uv run python scripts/generate_sample_data.py
uv run eraa-viz
```

Die HTML-Dateien liegen danach unter `output/` (bzw. unter den in `config.yaml` gesetzten Unterordnern).

## Erzeugte Visualisierungen

- **Adequacy**: LOLE- und ENS-Boxplots (pro Zone/Zieljahr), LOLE-Heatmap (Zone × Zieljahr)
- **Dispatch**: Zeitreihe Erzeugung nach Technologie, Heatmaps Erzeugung (Technologie × Zeit) pro Zone/Zieljahr
- **Net Position**: Zeitreihe und Heatmap (Zone × Zeit)
- **Preise**: Zeitreihe und Boxplot
- **Storage**: Zeitreihe Füllstand (level_pct/level_mwh)

Alle Plots sind interaktiv (Plotly) und werden als eigenständige HTML-Dateien gespeichert.

## Projektstruktur

```
eraa-data-visualizer/
├── config.yaml              # Konfiguration (Pfade, Schema, Visualisierung)
├── pyproject.toml            # UV/Python-Projekt und Abhängigkeiten
├── README.md
├── data/                     # Eingabedaten (CSV/Parquet)
├── output/                   # Ausgabe-HTML (adequacy/, dispatch/, …)
├── scripts/
│   └── generate_sample_data.py
└── src/
    └── eraa_visualizer/
        ├── __init__.py
        ├── config.py         # Config-Laden (Pydantic)
        ├── models.py         # Generisches Datenmodell (Adequacy, Dispatch, …)
        ├── loaders.py        # CSV/Parquet-Laden mit Schema-Mapping
        ├── plots.py          # Plotly-Plots (Box, Heatmap, Zeitreihe)
        ├── pipeline.py      # Hauptpipeline
        └── cli.py           # CLI (eraa-viz)
```

## Git und GitHub

Repository ist bereits initialisiert. **Hinweis:** GitHub erlaubt seit 2021 kein Passwort mehr für Git – du brauchst einen **Personal Access Token (PAT)** oder SSH.

### Erster Push

1. **Token erstellen:** [github.com/settings/tokens](https://github.com/settings/tokens) → „Generate new token (classic)“ → Scope **repo** → Token kopieren.
2. **Repo auf GitHub anlegen:** [github.com/new](https://github.com/new), Name z. B. `eraa-data-visualizer`, leer (ohne README).
3. **Remote auf deinen Benutzernamen setzen** (z. B. `fe111x`) und pushen:

```bash
git remote set-url origin https://github.com/fe111x/eraa-data-visualizer.git
git push -u origin main
```

Wenn Git nach **Username** fragt: dein GitHub-Benutzername (z. B. `fe111x`).  
Wenn Git nach **Password** fragt: den **Token** einfügen (nicht dein GitHub-Passwort).

## Lizenz

Projektbezogen (siehe Repository).
