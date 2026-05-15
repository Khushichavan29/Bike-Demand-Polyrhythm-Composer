# 🚲 Bike Demand Polyrhythm Composer

> Converts real urban cycling demand into layered rhythmic music.  
> Temporal patterns, weather signals, and seasonal flux become **MIDI**, **WAV**, and **visual rhythm exports** — driven entirely by `hour.csv`.

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Dataset](https://img.shields.io/badge/UCI-Bike%20Sharing%20Dataset-1D9E75?style=flat-square)](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset)

---

## Features

- Uses the **UCI Bike Sharing hourly dataset** as the primary input
- Cleans and normalizes temporal, demand, and weather signals
- Maps demand, time-of-day, season, and weather into **three polyrhythmic layers**
- Adds bass anchors and seasonal harmonic pads for richer arrangements
- Forecasts future bike demand and turns predictions into future rhythm exports
- Exports a playable `.mid` file **without relying on external MIDI libraries**
- Generates a stereo synthesized `.wav` preview and a rhythm timeline chart
- Includes a **Streamlit UI** with presets, groove controls, playback, preview, and downloads

---

## Project Structure

```
Bike Demand Polyrhythm Composer/
|-- composer/
|   |-- data_pipeline.py
|   |-- exporters.py
|   |-- rhythm_engine.py
|   `-- visualization.py
|-- data/
|   |-- hour.csv
|   `-- sample_bike_demand.csv
|-- outputs/
|-- app.py
|-- main.py
`-- requirements.txt
```

---

## UCI Dataset

**Primary source:**

- **<https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset>**

**Expected UCI hourly columns:**

| Column | Description |
|---|---|
| `dteday` | Date |
| `hr` | Hour (0–23) |
| `cnt` | Total bike rentals |
| `season` | Season (1–4) |
| `temp` | Normalized temperature |
| `hum` | Normalized humidity |
| `windspeed` | Normalized wind speed |
| `workingday` / `weekday` | Working day flag |

The importer also accepts the internal normalized format:

| Column | Description |
|---|---|
| `datetime` | Combined timestamp |
| `count` | Demand count |
| `temperature` | Normalized temp |
| `humidity` | Normalized humidity |
| `windspeed` | Normalized wind speed |
| `season` | Season (1–4) |
| `is_weekend` | Weekend flag |

---

## Signal → Music Mapping

| Dataset Signal | Musical Output |
|---|---|
| `cnt` — demand intensity | Note velocity |
| `hr` — hour of day | Rhythmic energy |
| `temp` | Pitch register |
| `hum` — humidity | Accent layer shape |
| `windspeed` | High-register weather layer |
| `season` (1–4) | MIDI instrument program |

---

## Run

**Install dependencies:**

```bash
python -m pip install -r requirements.txt
```

Place the UCI `hour.csv` file inside `data/`, then run:

```bash
python main.py --input data/hour.csv --steps 24
```

To forecast future demand and compose prediction-based rhythms:

```bash
python main.py --input data/hour.csv --steps 24 --predict-hours 24 --preset "Commute Rush"
```

To launch the Streamlit UI:

```bash
streamlit run app.py
```

---

## Streamlit Interface

The interface lets you:

- Use the bundled sample or upload the UCI `hour.csv`
- Choose how many rows to sonify
- Select presets like `Commute Rush`, `Weekend Flow`, and `Rainy Day`
- Adjust density, swing, tempo, and accent strength
- Forecast **0 to 72 future hours** with an ML-based prediction layer
- Preview normalized data and demand curves
- Compare **historical vs predicted demand** inside the Prediction Lab
- Listen to the generated WAV audio
- Download current and future WAV / MIDI / chart exports

---

## Generated Outputs

All files are written to `outputs/`:

| File | Description |
|---|---|
| `bike_polyrhythm.mid` | Playable MIDI composition |
| `bike_polyrhythm.wav` | Stereo synthesized audio preview |
| `bike_polyrhythm.png` | Rhythm timeline chart |

---

## Processing Pipeline

```
hour.csv
   │
   ▼
① Data ingestion ──── parse dteday+hr, align column aliases, drop nulls
   │
   ▼
② Signal normalization ── scale demand, temp, hum, windspeed → [0, 1]
   │
   ▼
③ Rhythm engine ──── map signals to 3 polyrhythmic layers + groove controls
   │
   ├──▶ ④ Forecasting layer ── ML demand projection (up to 72 hrs ahead)
   │
   ▼
⑤ Export ──── MIDI · WAV · PNG → outputs/
```

---

## Future Extensions

- Support live urban mobility feeds for **real-time sonification**
- Add more instrument presets and tuning scales per season
- Export to **Ableton Live / DAW** compatible formats
- Web-based playback with interactive beat-grid editor

