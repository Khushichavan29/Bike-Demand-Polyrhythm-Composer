from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class PreparedDataset:
    frame: pd.DataFrame
    demand_min: float
    demand_max: float


GENERIC_REQUIRED_COLUMNS = {
    "datetime",
    "count",
    "temperature",
    "humidity",
    "windspeed",
    "season",
    "is_weekend",
}

UCI_HOURLY_REQUIRED_COLUMNS = {
    "dteday",
    "hr",
    "season",
    "temp",
    "hum",
    "windspeed",
    "cnt",
}


def load_dataset(csv_path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(csv_path)
    frame = normalize_dataset_schema(frame)
    missing = GENERIC_REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Dataset is missing required columns after normalization: {missing_text}")
    return frame


def normalize_dataset_schema(frame: pd.DataFrame) -> pd.DataFrame:
    columns = set(frame.columns)
    if GENERIC_REQUIRED_COLUMNS.issubset(columns):
        return frame.copy()
    if UCI_HOURLY_REQUIRED_COLUMNS.issubset(columns):
        return _normalize_uci_hourly(frame)
    raise ValueError(
        "Unsupported dataset schema. Provide either the project CSV format or the UCI Bike Sharing `hour.csv` file."
    )


def prepare_dataset(frame: pd.DataFrame) -> PreparedDataset:
    clean = frame.copy()
    clean["datetime"] = pd.to_datetime(clean["datetime"], errors="coerce")
    clean = clean.dropna(subset=["datetime", "count"])
    clean = clean.sort_values("datetime").reset_index(drop=True)

    numeric_columns = ["count", "temperature", "humidity", "windspeed"]
    for column in numeric_columns:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")
        clean[column] = clean[column].interpolate(limit_direction="both")
        clean[column] = clean[column].fillna(clean[column].median())

    clean["season"] = clean["season"].fillna("unknown").astype(str).str.lower()
    clean["is_weekend"] = clean["is_weekend"].fillna(0).astype(int).clip(0, 1)
    clean["hour"] = clean["datetime"].dt.hour
    clean["day_of_week"] = clean["datetime"].dt.dayofweek
    clean["month"] = clean["datetime"].dt.month
    clean["day_name"] = clean["datetime"].dt.day_name()
    clean["demand_norm"] = _minmax(clean["count"])
    clean["temp_norm"] = _minmax(clean["temperature"])
    clean["humidity_norm"] = _minmax(clean["humidity"])
    clean["wind_norm"] = _minmax(clean["windspeed"])

    return PreparedDataset(
        frame=clean,
        demand_min=float(clean["count"].min()),
        demand_max=float(clean["count"].max()),
    )


def _minmax(series: pd.Series) -> pd.Series:
    minimum = float(series.min())
    maximum = float(series.max())
    if maximum == minimum:
        return pd.Series([0.5] * len(series), index=series.index, dtype=float)
    return (series - minimum) / (maximum - minimum)


def _normalize_uci_hourly(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized["datetime"] = pd.to_datetime(normalized["dteday"]) + pd.to_timedelta(
        normalized["hr"], unit="h"
    )
    normalized["count"] = normalized["cnt"]
    normalized["temperature"] = normalized["temp"] * 41
    normalized["humidity"] = normalized["hum"] * 100
    normalized["windspeed"] = normalized["windspeed"] * 67
    normalized["season"] = normalized["season"].map(
        {
            1: "spring",
            2: "summer",
            3: "fall",
            4: "winter",
        }
    ).fillna("unknown")
    if "workingday" in normalized.columns:
        normalized["is_weekend"] = (1 - normalized["workingday"]).clip(lower=0, upper=1)
    elif "weekday" in normalized.columns:
        normalized["is_weekend"] = normalized["weekday"].isin([0, 6]).astype(int)
    else:
        normalized["is_weekend"] = normalized["datetime"].dt.dayofweek.isin([5, 6]).astype(int)

    return normalized[
        [
            "datetime",
            "count",
            "temperature",
            "humidity",
            "windspeed",
            "season",
            "is_weekend",
        ]
    ]
