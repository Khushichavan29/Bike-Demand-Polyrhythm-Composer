# Bike Demand Polyrhythm Composer

Bike Demand Polyrhythm Composer converts the UCI Machine Learning Repository Bike Sharing Dataset into layered rhythmic music. The project is designed around the official hourly file `hour.csv` and produces MIDI, WAV, and visualization outputs from real bike-demand patterns.

## Features

- Uses the UCI Bike Sharing hourly dataset as the primary input
- Cleans and normalizes temporal, demand, and weather signals
- Maps demand, time-of-day, season, and weather into three polyrhythmic layers
- Adds bass anchors and seasonal harmonic pads for richer arrangements
- Forecasts future bike demand and turns predictions into future rhythm exports
- Exports a playable `.mid` file without relying on external MIDI libraries
- Generates a stereo synthesized `.wav` preview and a rhythm timeline chart
- Includes a Streamlit UI with presets, groove controls, playback, preview, and downloads

## Project Structure

```text
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

## UCI Dataset

Primary source:

- https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset

Expected UCI hourly columns:

- `dteday`
- `hr`
- `cnt`
- `season`
- `temp`
- `hum`
- `windspeed`
- `workingday` or `weekday`

The importer also accepts the internal normalized format:

- `datetime`
- `count`
- `temperature`
- `humidity`
- `windspeed`
- `season`
- `is_weekend`

## Run

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Place the UCI `hour.csv` file inside `data/`, then run:

```powershell
python main.py --input data/hour.csv --steps 24
```

To forecast future demand and compose prediction-based rhythms:

```powershell
python main.py --input data/hour.csv --steps 24 --predict-hours 24 --preset "Commute Rush"
```

To launch the Streamlit UI:

```powershell
streamlit run app.py
```

The interface lets you:

- Use the bundled sample or upload the UCI `hour.csv`
- Choose how many rows to sonify
- Select presets like `Commute Rush`, `Weekend Flow`, and `Rainy Day`
- Adjust density, swing, tempo, and accent strength
- Forecast 0 to 72 future hours with an ML-based prediction layer
- Preview normalized data and demand curves
- Compare historical vs predicted demand inside the Prediction Lab
- Listen to the generated WAV audio
- Download current and future WAV/MIDI/chart exports

Generated files are written to `outputs/`:

- `bike_polyrhythm.mid`
- `bike_polyrhythm.wav`
- `bike_polyrhythm.png`

## Mapping Logic

- Demand intensity controls note velocity
- Hour of day changes rhythmic energy
- Temperature shifts pitch register
- Humidity shapes the accent layer
- Windspeed shapes the high-register weather layer
- Season selects the MIDI instrument program

## Future Extensions

- Add demand prediction for future music generation
- Support live urban mobility feeds for real-time sonification
