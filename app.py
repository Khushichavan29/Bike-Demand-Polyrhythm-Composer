from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import streamlit as st

from composer.pipeline import run_pipeline
from composer.rhythm_engine import LAYER_LABELS, PRESET_LIBRARY, SEASON_PROGRAM, build_settings


st.set_page_config(
    page_title="Bike Demand Polyrhythm Composer",
    page_icon="B",
    layout="wide",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 10% 10%, rgba(255, 196, 82, 0.22), transparent 28%),
                radial-gradient(circle at 92% 18%, rgba(52, 152, 219, 0.16), transparent 30%),
                linear-gradient(180deg, #f5eee1 0%, #e9f0f2 100%);
        }
        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 2.5rem;
        }
        .hero {
            padding: 1.8rem 1.8rem 1.6rem 1.8rem;
            border-radius: 28px;
            background:
                radial-gradient(circle at top right, rgba(253, 186, 116, 0.22), transparent 30%),
                linear-gradient(135deg, #0f172a 0%, #1f2937 55%, #334155 100%);
            color: #f8fafc;
            box-shadow: 0 24px 48px rgba(15, 23, 42, 0.16);
            margin-bottom: 1.2rem;
        }
        .hero h1 {
            font-size: 2.4rem;
            margin-bottom: 0.25rem;
        }
        .hero p {
            margin: 0;
            max-width: 820px;
            line-height: 1.65;
            color: rgba(248, 250, 252, 0.86);
        }
        .glass-card {
            padding: 1rem 1.05rem;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.74);
            border: 1px solid rgba(15, 23, 42, 0.08);
            box-shadow: 0 16px 40px rgba(148, 163, 184, 0.16);
        }
        .mini-label {
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: #64748b;
        }
        .big-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #0f172a;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>Bike Demand Polyrhythm Composer</h1>
            <p>
                Turn the UCI Bike Sharing Dataset into a living score. This studio-style interface
                lets you shape groove density, swing, and accent behavior while watching urban demand
                become bass anchors, weather sparks, pulse grids, and seasonal harmonic pads.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_sidebar() -> dict[str, object]:
    st.sidebar.header("Composition Studio")
    input_mode = st.sidebar.radio(
        "Dataset Source",
        ["Bundled sample", "Upload UCI hour.csv"],
        index=0,
    )
    preset_name = st.sidebar.selectbox(
        "Creative Preset",
        list(PRESET_LIBRARY.keys()),
        index=0,
    )
    steps = st.sidebar.slider("Rows to sonify", min_value=8, max_value=168, value=24, step=4)
    prediction_horizon = st.sidebar.slider("Future prediction hours", min_value=0, max_value=72, value=24, step=6)
    tempo_boost = st.sidebar.slider("Tempo boost", min_value=-24, max_value=24, value=0, step=2)
    density = st.sidebar.slider("Rhythm density", min_value=0.7, max_value=1.6, value=1.0, step=0.1)
    swing = st.sidebar.slider("Swing amount", min_value=0.0, max_value=0.18, value=0.02, step=0.01)
    accent_strength = st.sidebar.slider("Accent strength", min_value=0.8, max_value=1.4, value=1.0, step=0.1)
    show_table = st.sidebar.checkbox("Show normalized dataset preview", value=True)

    st.sidebar.caption(
        "Presets give the composition a musical identity, while the sliders let you fine-tune the sonification."
    )
    return {
        "input_mode": input_mode,
        "preset_name": preset_name,
        "steps": steps,
        "prediction_horizon": prediction_horizon,
        "tempo_boost": tempo_boost,
        "density": density,
        "swing": swing,
        "accent_strength": accent_strength,
        "show_table": show_table,
    }


def resolve_input_file(input_mode: str) -> Path | None:
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    sample_path = data_dir / "hour.csv"
    if input_mode == "Bundled sample":
        return sample_path

    uploaded = st.sidebar.file_uploader("Upload `hour.csv`", type=["csv"])
    if uploaded is None:
        return None

    upload_target = data_dir / uploaded.name
    upload_target.write_bytes(uploaded.getvalue())
    return upload_target


def render_metric_cards(payload: dict[str, object]) -> None:
    cards = st.columns(6)
    metrics = [
        ("Rows Used", str(payload["rows_used"])),
        ("Tempo", f"{payload['tempo_bpm']} BPM"),
        ("Demand Span", f"{payload['demand_min']:.0f} to {payload['demand_max']:.0f}"),
        ("Notes", str(payload["notes_count"])),
        ("Preset", str(payload["preset_name"])),
        ("Prediction", f"{payload['prediction_horizon']}h"),
    ]
    for column, (label, value) in zip(cards, metrics):
        column.markdown(
            f"<div class='glass-card'><div class='mini-label'>{label}</div><div class='big-value'>{value}</div></div>",
            unsafe_allow_html=True,
        )


def render_overview(payload: dict[str, object]) -> None:
    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("Demand Curve")
        demand_frame = payload["prepared_frame"][["datetime", "count"]].copy().set_index("datetime")
        st.line_chart(demand_frame)

        if payload["chart_bytes"] is not None:
            st.subheader("Polyrhythm Timeline")
            st.image(payload["chart_bytes"], use_container_width=True)
        else:
            st.info("Install `matplotlib` to render the full rhythm timeline chart.")

    with right:
        st.subheader("Composition DNA")
        st.markdown(
            "\n".join(
                [
                    f"- Preset: `{payload['preset_name']}`",
                    f"- Density factor: `{payload['density']:.2f}`",
                    f"- Swing amount: `{payload['swing']:.2f}`",
                    f"- Accent strength: `{payload['accent_strength']:.2f}`",
                    f"- Prediction model: `{payload['prediction_model']}`",
                    f"- Seasonal instruments available: `{', '.join(sorted(SEASON_PROGRAM))}`",
                ]
            )
        )
        st.subheader("Generated Layers")
        layer_counts = payload["layer_counts"]
        for layer, count in layer_counts.items():
            label = LAYER_LABELS.get(layer, layer)
            st.progress(min(1.0, count / max(layer_counts.values())), text=f"{label}: {count} notes")

        st.subheader("Layer Snapshots")
        st.code("\n".join(payload["layer_summaries"][:8]), language="text")


def render_mapping_lab(payload: dict[str, object], show_table: bool) -> None:
    tab1, tab2, tab3, tab4 = st.tabs(["Mapping Logic", "Dataset Preview", "Prediction Lab", "Export Studio"])

    with tab1:
        mapping_cols = st.columns(2)
        mapping_cols[0].markdown(
            "\n".join(
                [
                    "### Data to music",
                    "- Demand intensity drives pulse velocity and bass emphasis.",
                    "- Commute hours increase kinetic energy and perceived urgency.",
                    "- Temperature shifts the harmonic center upward or downward.",
                    "- Humidity reshapes accents into tighter or softer patterns.",
                    "- Windspeed adds glittering high-register weather events.",
                ]
            )
        )
        mapping_cols[1].markdown(
            "\n".join(
                [
                    "### Musical design",
                    "- `Demand Pulse` acts as the rhythmic spine.",
                    "- `Clock Grid` reflects time structure and weekday behavior.",
                    "- `Weather Spark` introduces upper-register motion.",
                    "- `Mobility Bass` grounds high-demand moments.",
                    "- `Season Pad` turns context into harmony.",
                ]
            )
        )

    with tab2:
        if show_table:
            preview_columns = [
                "datetime",
                "count",
                "season",
                "is_weekend",
                "hour",
                "demand_norm",
                "temp_norm",
                "humidity_norm",
                "wind_norm",
            ]
            st.dataframe(payload["prepared_frame"][preview_columns].head(24), use_container_width=True)
        else:
            st.info("Enable `Show normalized dataset preview` from the sidebar to inspect processed rows.")

    with tab3:
        if payload["prediction_horizon"] <= 0 or payload["future_frame"] is None:
            st.info("Set `Future prediction hours` above 0 to forecast demand and compose future rhythms.")
        else:
            pred_left, pred_right = st.columns([1.3, 1])
            with pred_left:
                combined = pd.concat(
                    [
                        payload["historical_tail"][["datetime", "count"]].assign(series="Historical"),
                        payload["future_frame"][["datetime", "count"]].assign(series="Predicted"),
                    ],
                    ignore_index=True,
                )
                chart_source = combined.pivot(index="datetime", columns="series", values="count")
                st.line_chart(chart_source)
                if payload["prediction_chart_bytes"] is not None:
                    st.image(payload["prediction_chart_bytes"], use_container_width=True)
            with pred_right:
                st.markdown(
                    "\n".join(
                        [
                            "### Forecast summary",
                            f"- Model used: `{payload['prediction_model']}`",
                            f"- Future rows: `{len(payload['future_frame'])}`",
                            f"- Predicted demand range: `{payload['future_min']:.0f}` to `{payload['future_max']:.0f}`",
                            f"- Future tempo: `{payload['future_tempo_bpm']} BPM`",
                        ]
                    )
                )
                st.dataframe(
                    payload["future_frame"][["datetime", "count", "season", "is_weekend"]].head(12),
                    use_container_width=True,
                )

        st.subheader("Future Layer Snapshots")
        if payload["future_layer_summaries"]:
            st.code("\n".join(payload["future_layer_summaries"][:8]), language="text")
        else:
            st.caption("No future composition generated.")

    with tab4:
        cols = st.columns(4)
        cols[0].audio(payload["wav_bytes"], format="audio/wav")
        cols[0].download_button(
            "Download WAV",
            data=payload["wav_bytes"],
            file_name="bike_polyrhythm.wav",
            mime="audio/wav",
            use_container_width=True,
        )
        cols[1].download_button(
            "Download MIDI",
            data=payload["midi_bytes"],
            file_name="bike_polyrhythm.mid",
            mime="audio/midi",
            use_container_width=True,
        )
        if payload["future_wav_bytes"] is not None:
            cols[2].audio(payload["future_wav_bytes"], format="audio/wav")
            cols[2].download_button(
                "Download Future WAV",
                data=payload["future_wav_bytes"],
                file_name="bike_polyrhythm_future.wav",
                mime="audio/wav",
                use_container_width=True,
            )
            cols[3].download_button(
                "Download Future MIDI",
                data=payload["future_midi_bytes"],
                file_name="bike_polyrhythm_future.mid",
                mime="audio/midi",
                use_container_width=True,
            )
        else:
            cols[2].info("Future exports appear when prediction is enabled.")
            cols[3].info("Future exports appear when prediction is enabled.")

        if payload["chart_bytes"] is not None or payload["prediction_chart_bytes"] is not None:
            extra = st.columns(2)
            if payload["chart_bytes"] is not None:
                extra[0].download_button(
                    "Download Rhythm Chart",
                    data=payload["chart_bytes"],
                    file_name="bike_polyrhythm.png",
                    mime="image/png",
                    use_container_width=True,
                )
            if payload["prediction_chart_bytes"] is not None:
                extra[1].download_button(
                    "Download Prediction Chart",
                    data=payload["prediction_chart_bytes"],
                    file_name="bike_demand_prediction.png",
                    mime="image/png",
                    use_container_width=True,
                )


def stash_result(result, settings, steps: int) -> None:
    layer_counts: dict[str, int] = {}
    for note in result.composition.notes:
        layer_counts[note.layer] = layer_counts.get(note.layer, 0) + 1

    st.session_state["composition_result"] = {
        "prepared_frame": result.prepared.frame.copy(),
        "demand_min": result.prepared.demand_min,
        "demand_max": result.prepared.demand_max,
        "tempo_bpm": result.composition.tempo_bpm,
        "rows_used": min(steps, len(result.prepared.frame)),
        "notes_count": len(result.composition.notes),
        "layer_counts": layer_counts,
        "layer_summaries": result.composition.layer_summaries,
        "preset_name": settings.preset_name,
        "density": settings.density,
        "swing": settings.swing,
        "accent_strength": settings.accent_strength,
        "prediction_horizon": 0 if result.prediction is None else len(result.prediction.future_frame),
        "prediction_model": "disabled" if result.prediction is None else result.prediction.model_name,
        "historical_tail": result.prepared.frame.tail(min(len(result.prepared.frame), 72)).copy(),
        "future_frame": None if result.future_prepared is None else result.future_prepared.frame.copy(),
        "future_min": None if result.future_prepared is None else result.future_prepared.demand_min,
        "future_max": None if result.future_prepared is None else result.future_prepared.demand_max,
        "future_tempo_bpm": None if result.future_composition is None else result.future_composition.tempo_bpm,
        "future_layer_summaries": [] if result.future_composition is None else result.future_composition.layer_summaries,
        "midi_bytes": result.midi_path.read_bytes(),
        "wav_bytes": result.wav_path.read_bytes(),
        "chart_bytes": result.chart_path.read_bytes() if result.chart_path is not None else None,
        "future_midi_bytes": None if result.future_midi_path is None else result.future_midi_path.read_bytes(),
        "future_wav_bytes": None if result.future_wav_path is None else result.future_wav_path.read_bytes(),
        "prediction_chart_bytes": None if result.prediction_chart_path is None else result.prediction_chart_path.read_bytes(),
    }


def render_stashed_result(show_table: bool) -> None:
    payload = st.session_state.get("composition_result")
    if payload is None:
        return
    render_metric_cards(payload)
    render_overview(payload)
    render_mapping_lab(payload, show_table)


def main() -> None:
    inject_styles()
    render_header()
    controls = build_sidebar()
    input_path = resolve_input_file(controls["input_mode"])

    if input_path is None:
        st.info("Upload the UCI `hour.csv` file from the sidebar to begin.")
        return

    if not input_path.exists():
        st.error(f"Dataset not found at {input_path}. Add the UCI `hour.csv` file to the `data/` folder.")
        return

    settings = build_settings(
        preset_name=str(controls["preset_name"]),
        tempo_boost=int(controls["tempo_boost"]),
        density=float(controls["density"]),
        swing=float(controls["swing"]),
        accent_strength=float(controls["accent_strength"]),
    )

    st.caption(
        f"Current preset: `{settings.preset_name}` with density `{settings.density:.2f}`, "
        f"swing `{settings.swing:.2f}`, and accent strength `{settings.accent_strength:.2f}`."
    )

    if st.button("Compose Polyrhythm", type="primary", use_container_width=True):
        with st.spinner("Arranging bike demand into a richer musical structure..."):
            try:
                with TemporaryDirectory() as temp_dir:
                    result = run_pipeline(
                        input_path,
                        temp_dir,
                        int(controls["steps"]),
                        settings=settings,
                        prediction_horizon=int(controls["prediction_horizon"]),
                    )
                    stash_result(result, settings, int(controls["steps"]))
            except Exception as error:
                st.exception(error)

    if st.session_state.get("composition_result") is not None:
        render_stashed_result(bool(controls["show_table"]))
    else:
        st.subheader("Input Snapshot")
        st.dataframe(pd.read_csv(input_path).head(10), use_container_width=True)
        st.caption("Choose a preset, tune the groove controls, and click `Compose Polyrhythm`.")


if __name__ == "__main__":
    main()
