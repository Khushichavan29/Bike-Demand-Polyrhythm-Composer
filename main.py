from __future__ import annotations

import argparse

from composer.pipeline import run_pipeline
from composer.rhythm_engine import PRESET_LIBRARY, build_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transform bike demand data into a polyrhythmic composition."
    )
    parser.add_argument(
        "--input",
        default="data/hour.csv",
        help="Path to the bike demand CSV file.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory for generated MIDI, WAV, and chart files.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=24,
        help="How many rows of the dataset to transform into music.",
    )
    parser.add_argument(
        "--preset",
        default="Balanced Study",
        choices=list(PRESET_LIBRARY.keys()),
        help="Composition preset to guide groove and arrangement.",
    )
    parser.add_argument(
        "--tempo-boost",
        type=int,
        default=0,
        help="Additional BPM adjustment applied on top of the preset.",
    )
    parser.add_argument(
        "--predict-hours",
        type=int,
        default=0,
        help="Forecast this many future hours and generate future rhythm exports.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = build_settings(
        preset_name=args.preset,
        tempo_boost=args.tempo_boost,
        density=1.0,
        swing=0.0,
        accent_strength=1.0,
    )
    result = run_pipeline(
        args.input,
        args.output_dir,
        args.steps,
        settings=settings,
        prediction_horizon=args.predict_hours,
    )

    print("Bike Demand Polyrhythm Composer completed successfully.")
    print(f"Input rows used: {min(args.steps, len(result.prepared.frame))}")
    print(f"Demand range: {result.prepared.demand_min:.0f} to {result.prepared.demand_max:.0f}")
    print(f"Tempo: {result.composition.tempo_bpm} BPM")
    print(f"Preset: {result.composition.settings.preset_name}")
    print(f"MIDI: {result.midi_path}")
    print(f"WAV: {result.wav_path}")
    if result.chart_path is not None:
        print(f"Chart: {result.chart_path}")
    else:
        print("Chart: skipped because matplotlib is not installed.")
    if result.prediction is not None and result.future_composition is not None:
        print(f"Prediction model: {result.prediction.model_name}")
        print(f"Future tempo: {result.future_composition.tempo_bpm} BPM")
        print(f"Future MIDI: {result.future_midi_path}")
        print(f"Future WAV: {result.future_wav_path}")
        if result.prediction_chart_path is not None:
            print(f"Prediction chart: {result.prediction_chart_path}")


if __name__ == "__main__":
    main()
