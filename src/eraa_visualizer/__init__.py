"""
ERAA Data Visualizer – Visualisierungspipeline für European Resource Adequacy Assessment.

Unterstützt:
- Adequacy (LOLE, ENS, EENS, LLD, Perzentile)
- Economic Dispatch (Erzeugung/Laden nach PEMMDB-Typ)
- Net Position (alle Marktgebiete)
- Preise
- Speicher und Füllstände

Typische Modellstruktur: 36 Klimajahre × 10 Samples (Outage-Patterns) pro Zieljahr.
"""

__version__ = "0.1.0"
