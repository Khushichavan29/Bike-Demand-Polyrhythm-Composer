# Bike-Demand-Polyrhythm-Composer
Converts real urban cycling demand into layered rhythmic music. Temporal patterns, weather signals, and seasonal flux become MIDI, WAV, and visual rhythm exports — driven entirely by hour.csv.

Features:
1. UCI dataset ingestion — reads the official hour.csv directly, cleaning and normalizing temporal, demand, and weather signals automatically.
2. Three polyrhythmic layers — demand intensity, time-of-day energy, and weather accent form independent rhythms that phase against each other.
3. Bass anchors + seasonal pads — bass notes ground each pattern while MIDI instrument programs shift by season for harmonic color.
4. ML demand forecasting — predict 1–72 future hours and convert those predictions into their own rhythm exports via --predict-hours.
5. Zero-dependency MIDI export — writes a playable .mid file without any external MIDI library.
6. Stereo WAV preview — synthesizes a full stereo audio preview alongside a rhythm timeline chart at outputs/.

Ptoject Stucture:
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

UCI Dataset

https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset

Run
Install dependencies:

python -m pip install -r requirements.txt
Place the UCI hour.csv file inside data/, then run:

python main.py --input data/hour.csv --steps 24
To forecast future demand and compose prediction-based rhythms:

python main.py --input data/hour.csv --steps 24 --predict-hours 24 --preset "Commute Rush"
To launch the Streamlit UI:

streamlit run app.py
The interface lets you:

Use the bundled sample or upload the UCI hour.csv
Choose how many rows to sonify
Select presets like Commute Rush, Weekend Flow, and Rainy Day
Adjust density, swing, tempo, and accent strength
Forecast 0 to 72 future hours with an ML-based prediction layer
Preview normalized data and demand curves
Compare historical vs predicted demand inside the Prediction Lab
Listen to the generated WAV audio
Download current and future WAV/MIDI/chart exports
Generated files are written to outputs/:

bike_polyrhythm.mid
bike_polyrhythm.wav
bike_polyrhythm.png
