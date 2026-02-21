# ERAA – Hintergrund und Datenstruktur

## Was ist ERAA?

Das **European Resource Adequacy Assessment (ERAA)** ist die paneuropäische Bewertung der **Versorgungsadequacy** durch ENTSO-E (European Network of Transmission System Operators for Electricity). Es bewertet die Ressourcenadequacy bis zu **10 Jahre im Voraus** und nutzt dabei probabilistische Methoden (Monte-Carlo-Simulationen über viele Klimajahre und Outage-Samples).

- **Rechtliche Grundlage**: EU-Verordnung 2019/943, Methodik von ACER (Decision 23-2020) genehmigt.
- **Zweck**: Fundierte Entscheidungen zu Kapazitätsmechanismen, strategische Planung, Erkennung von Adequacy-Risiken.
- **Typische Kennzahlen**: LOLE (Loss of Load Expectation) in h/Jahr, ENS (Energy Not Served) in GWh, sowie EENS und Perzentile (P50, P95).

## Warum 36 Klimajahre × 10 Samples?

- **Klimajahre**: Unterschiedliche Wetterjahre (Wind, Sonne, Last) führen zu unterschiedlichen RES-Erzeugungen und Lasten. Ein einzelnes Jahr reicht für eine stabile LOLE-Schätzung nicht aus.
- **Samples**: Verschiedene **Outage-Patterns** (Kraftwerksausfälle, Wartung) werden stochastisch erzeugt. Pro Klimajahr werden mehrere Samples (z. B. 10) simuliert.
- **Ergebnis**: Pro Zieljahr und Zone liegen typischerweise **36 × 10 = 360** Wertepaare (LLD, ENS) vor, aus denen LOLE (Mittelwert der LLD), EENS, P50 und P95 abgeleitet werden.

## PEMMDB (Pan-European Market Modelling Database)

Die **PEMMDB** ist die einheitliche Datenbasis für die Modellierung europäischer Strommärkte im ERAA-Kontext. Sie definiert u. a.:

- **Technologietypen** für Erzeugung: Nuclear, Lignite, Hard Coal, Gas CCGT, Gas OCGT, Oil, Biomass, Hydro (Laufwasser, Speicher, Pumpspeicher), Wind Onshore/Offshore, Solar, DSR (Demand-Side Response) usw.
- **Speicher**: Battery, Hydro Pumped Storage u. a.
- **Study Zones** (Marktgebiete): z. B. AT00, BE00, DE00, FR00, NL00, PL00, …

Die Daten werden von den TSOs bereitgestellt und in der PEMMDB-Anwendung (OWL/Excel-basiert) gepflegt.

## Klassische Modell-Outputs (für diese Pipeline)

| Kategorie | Inhalt | Dimensionen |
|-----------|--------|-------------|
| **Adequacy** | LOLE, EENS, LLD, ENS, P50/P95 | study_zone, target_year, scenario, climate_year, sample_id |
| **Economic Dispatch** | Erzeugung (MW) und Ladung (z. B. Pumpspeicher) pro Technologie | study_zone, target_year, technology, datetime, climate_year, sample_id |
| **Net Position** | Netto-Import/Export pro Marktgebiet (MW) | study_zone, target_year, datetime, climate_year, sample_id |
| **Preise** | Strompreis (€/MWh) | study_zone, target_year, datetime, climate_year, sample_id |
| **Speicher** | Füllstände (%, MWh) pro Speichertyp | study_zone, target_year, storage_type, datetime, climate_year, sample_id |

Die Visualisierungspipeline baut auf diesem **generischen Datenmodell** auf und erlaubt über `config.yaml` Anpassungen an unterschiedliche Spaltennamen und Modellvarianten.

## Quellen

- [ENTSO-E ERAA](https://www.entsoe.eu/eraa/)
- [ERAA 2024 Modelling data](https://www.entsoe.eu/eraa/2024/modelling-data)
- ENTSO-E ERAA 2023 Annex 3: Detailed Results (LOLE/ENS-Tabellen, EVA, Study Zones)
- ACER ERAA Methodology (Annex zu ACER Decision 23-2020 bzw. 07-2025 für ERAA 2024)
- PEMMDB: ENTSO-E Data Collection Guidelines (ERAA/TYNDP)
