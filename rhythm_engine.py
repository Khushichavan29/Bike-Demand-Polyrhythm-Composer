from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .data_pipeline import PreparedDataset, load_dataset, prepare_dataset
from .exporters import export_midi, export_wav
from .predictor import PredictionResult, forecast_future_demand
from .rhythm_engine import Composition, CompositionSettings, build_composition
from .visualization import plot_demand_and_layers, plot_prediction_comparison


@dataclass
class PipelineResult:
    prepared: PreparedDataset
    composition: Composition
    midi_path: Path
    wav_path: Path
    chart_path: Path | None
    prediction: PredictionResult | None
    future_prepared: PreparedDataset | None
    future_composition: Composition | None
    future_midi_path: Path | None
    future_wav_path: Path | None
    prediction_chart_path: Path | None


def run_pipeline(
    input_source: str | Path,
    output_dir: str | Path,
    steps: int,
    settings: CompositionSettings | None = None,
    prediction_horizon: int = 0,
) -> PipelineResult:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    frame = load_dataset(input_source)
    prepared = prepare_dataset(frame)
    composition = build_composition(prepared.frame, steps=steps, settings=settings)

    midi_path = export_midi(composition, output_path / "bike_polyrhythm.mid")
    wav_path = export_wav(composition, output_path / "bike_polyrhythm.wav")

    chart_path = None
    prediction = None
    future_prepared = None
    future_composition = None
    future_midi_path = None
    future_wav_path = None
    prediction_chart_path = None
    try:
        chart_path = plot_demand_and_layers(
            prepared.frame.head(steps),
            composition,
            output_path / "bike_polyrhythm.png",
        )
    except ModuleNotFoundError as error:
        if error.name != "matplotlib":
            raise

    if prediction_horizon > 0:
        prediction = forecast_future_demand(prepared.frame, prediction_horizon)
        future_prepared = prepare_dataset(prediction.future_frame)
        future_composition = build_composition(
            future_prepared.frame,
            steps=min(prediction_horizon, len(future_prepared.frame)),
            settings=settings,
        )
        future_midi_path = export_midi(future_composition, output_path / "bike_polyrhythm_future.mid")
        future_wav_path = export_wav(future_composition, output_path / "bike_polyrhythm_future.wav")
        try:
            prediction_chart_path = plot_prediction_comparison(
                prepared.frame.tail(min(len(prepared.frame), 72)),
                future_prepared.frame,
                output_path / "bike_demand_prediction.png",
            )
        except ModuleNotFoundError as error:
            if error.name != "matplotlib":
                raise

    return PipelineResult(
        prepared=prepared,
        composition=composition,
        midi_path=midi_path,
        wav_path=wav_path,
        chart_path=chart_path,
        prediction=prediction,
        future_prepared=future_prepared,
        future_composition=future_composition,
        future_midi_path=future_midi_path,
        future_wav_path=future_wav_path,
        prediction_chart_path=prediction_chart_path,
    )
