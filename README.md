# Bike-Demand-Polyrhythm-Composer
Converts real urban cycling demand into layered rhythmic music. Temporal patterns, weather signals, and seasonal flux become MIDI, WAV, and visual rhythm exports — driven entirely by hour.csv.

Features:
UCI dataset ingestion — reads the official hour.csv directly, cleaning and normalizing temporal, demand, and weather signals automatically.
Three polyrhythmic layers — demand intensity, time-of-day energy, and weather accent form independent rhythms that phase against each other.
Bass anchors + seasonal pads — bass notes ground each pattern while MIDI instrument programs shift by season for harmonic color.
ML demand forecasting — predict 1–72 future hours and convert those predictions into their own rhythm exports via --predict-hours.
Zero-dependency MIDI export — writes a playable .mid file without any external MIDI library.
Stereo WAV preview — synthesizes a full stereo audio preview alongside a rhythm timeline chart at outputs/.

Processing pipeline:
