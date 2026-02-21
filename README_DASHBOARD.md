# ERAA Data Visualizer – Dashboard (Streamlit)

Das Dashboard zeigt alle ERAA-Visualisierungen in einer Web-App: **Adequacy (LOLE, ENS)**, **Dispatch (Erzeugung)**, **Net Position**, **Preise** und **Speicher**. Mit Filtern für Zieljahr und Study Zone, angelehnt an das [offizielle ERAA-Dashboard](https://www.entsoe.eu/eraa/2024/modelling-data) von ENTSO-E.

---

## Voraussetzungen

- **Python 3.9 oder neuer** (3.11 empfohlen). Unter macOS ist oft nur Python 3.7 vorinstalliert – dann funktioniert `pip3 install -r requirements.txt` nicht (pandas 2.x braucht Python 3.9+).

---

## 0. Python 3.11 installieren (falls nötig)

Wenn `python3 --version` **3.7** oder **3.8** anzeigt:

**Mit Homebrew (empfohlen):**
```bash
brew install python@3.11
```

Danach nutzen:
- **Python:** `python3.11` (oder `$(brew --prefix python@3.11)/bin/python3.11`)
- **pip:** `python3.11 -m pip install -r requirements.txt`

**Alternativ:** Installer von [python.org](https://www.python.org/downloads/) (macOS, Python 3.11 oder 3.12). Dann im Terminal den dort installierten Befehl verwenden (z. B. `python3.11`).

---

## 1. Abhängigkeiten installieren

**Ohne UV (mit Python 3.9+):**
```bash
cd /Users/Felix/Documents/eraa-data-visualizer
python3.11 -m pip install -r requirements.txt
```

(Falls dein Standard-`python3` schon 3.9+ ist: `pip3 install -r requirements.txt`.)

**Mit UV (falls installiert):**
```bash
uv sync
```

---

## 2. Beispieldaten erzeugen (falls noch nicht vorhanden)

Damit das Dashboard Daten anzeigen kann, müssen CSV-Dateien im Ordner `data/` liegen:

```bash
# Aus Projektroot – gleiche Python-Version wie beim pip install (z. B. python3.11)
python3.11 scripts/generate_sample_data.py
```

(Falls bei dir `python` existiert, geht auch `python scripts/...`.)

Es werden erzeugt: `data/adequacy.csv`, `data/dispatch.csv`, `data/net_position.csv`, `data/prices.csv`, `data/storage.csv`.

---

## 3. Dashboard starten

**Aus dem Projektroot** (Ordner mit `config.yaml` und `app/`):

```bash
# Ohne UV (gleiche Python-Version wie beim pip install, z. B. python3.11)
PYTHONPATH=src python3.11 -m streamlit run app/dashboard.py
```

`PYTHONPATH=src` sorgt dafür, dass das Modul `eraa_visualizer` gefunden wird.

**Mit UV (falls installiert):**
```bash
uv run streamlit run app/dashboard.py
```

---

## 4. Im Browser öffnen

Nach dem Start erscheint in der Konsole z. B.:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

- **Lokal:** Im Browser **http://localhost:8501** aufrufen.
- **Auf dem gleichen Rechner:** Einfach den Local URL im Browser öffnen.
- **Von einem anderen Gerät im Netz:** Die angezeigte **Network URL** verwenden (gleiches WLAN vorausgesetzt).

Das Dashboard lädt automatisch die Daten aus `data/` und zeigt sie in Tabs mit Filtern in der Sidebar.

---

## 5. Beenden

Im Terminal **Strg+C** drücken, um den Streamlit-Server zu beenden.

---

## Kurzreferenz

| Aktion              | Befehl (ohne UV, Python 3.11) |
|---------------------|-------------------------------|
| Abhängigkeiten      | `python3.11 -m pip install -r requirements.txt` |
| Beispieldaten       | `python3.11 scripts/generate_sample_data.py` |
| Dashboard starten   | `PYTHONPATH=src python3.11 -m streamlit run app/dashboard.py` |
| Im Browser öffnen  | **http://localhost:8501** |
| Stoppen             | Strg+C im Terminal |

Mit UV: `uv sync` und `uv run streamlit run app/dashboard.py`.

---

## Filter im Dashboard

- **Sidebar:** **Target Year** und **Study Zone** (Mehrfachauswahl). Nur ausgewählte Jahre und Zonen werden in allen Tabs berücksichtigt.
- **Tab Dispatch:** Zusätzlich Auswahl für Zone und Zieljahr der Zeitreihe sowie Zone/Jahr für die Heatmap.

Eigene Daten: CSV- oder Parquet-Dateien mit den in `config.yaml` beschriebenen Spalten in den Ordner `data/` legen und das Dashboard neu laden (F5 oder „Rerun“ in Streamlit).
