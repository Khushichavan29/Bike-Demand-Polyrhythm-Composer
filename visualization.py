from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class PredictionResult:
    future_frame: pd.DataFrame
    model_name: str


def forecast_future_demand(frame: pd.DataFrame, horizon_hours: int) -> PredictionResult:
    if horizon_hours <= 0:
        return PredictionResult(future_frame=frame.iloc[0:0].copy(), model_name="disabled")

    future_base = _build_future_feature_frame(frame, horizon_hours)
    history = frame.copy().reset_index(drop=True)
    history["lag_1"] = history["count"].shift(1)
    history["lag_24"] = history["count"].shift(24)
    history["lag_168"] = history["count"].shift(168)
    history["rolling_24"] = history["count"].rolling(24, min_periods=1).mean().shift(1)
    history = history.dropna().reset_index(drop=True)

    if len(history) < 12:
        predicted = _naive_forecast(frame, future_base)
        return PredictionResult(future_frame=predicted, model_name="seasonal naive fallback")

    feature_columns = [
        "hour",
        "day_of_week",
        "month",
        "is_weekend",
        "temperature",
        "humidity",
        "windspeed",
        "lag_1",
        "lag_24",
        "lag_168",
        "rolling_24",
    ]

    try:
        from sklearn.ensemble import RandomForestRegressor

        model = RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            min_samples_leaf=2,
        )
        model.fit(history[feature_columns], history["count"])
        predicted = _roll_forward_predictions(frame, future_base, model, feature_columns)
        return PredictionResult(future_frame=predicted, model_name="RandomForestRegressor")
    except ModuleNotFoundError:
        predicted = _naive_forecast(frame, future_base)
        return PredictionResult(future_frame=predicted, model_name="seasonal naive fallback")


def _build_future_feature_frame(frame: pd.DataFrame, horizon_hours: int) -> pd.DataFrame:
    latest = frame.iloc[-1]
    start = latest["datetime"] + pd.Timedelta(hours=1)
    future_times = pd.date_range(start=start, periods=horizon_hours, freq="h")
    profile = frame.copy()
    profile["day_of_week"] = profile["datetime"].dt.dayofweek
    profile["month"] = profile["datetime"].dt.month

    hourly_weather = (
        profile.groupby("hour")[["temperature", "humidity", "windspeed"]]
        .median()
        .to_dict("index")
    )
    weekday_season = (
        profile.groupby("day_of_week")["season"]
        .agg(lambda values: values.mode().iat[0] if not values.mode().empty else profile["season"].iat[-1])
        .to_dict()
    )

    rows: list[dict[str, object]] = []
    for timestamp in future_times:
        hour = int(timestamp.hour)
        day_of_week = int(timestamp.dayofweek)
        weather = hourly_weather.get(
            hour,
            {
                "temperature": float(profile["temperature"].median()),
                "humidity": float(profile["humidity"].median()),
                "windspeed": float(profile["windspeed"].median()),
            },
        )
        rows.append(
            {
                "datetime": timestamp,
                "hour": hour,
                "day_of_week": day_of_week,
                "month": int(timestamp.month),
                "is_weekend": int(day_of_week >= 5),
                "temperature": float(weather["temperature"]),
                "humidity": float(weather["humidity"]),
                "windspeed": float(weather["windspeed"]),
                "season": weekday_season.get(day_of_week, str(profile["season"].iat[-1])),
            }
        )
    return pd.DataFrame(rows)


def _roll_forward_predictions(
    frame: pd.DataFrame,
    future_base: pd.DataFrame,
    model,
    feature_columns: list[str],
) -> pd.DataFrame:
    history_counts = list(frame["count"].astype(float))
    output = future_base.copy()

    for index, row in output.iterrows():
        features = {
            "hour": row["hour"],
            "day_of_week": row["day_of_week"],
            "month": row["month"],
            "is_weekend": row["is_weekend"],
            "temperature": row["temperature"],
            "humidity": row["humidity"],
            "windspeed": row["windspeed"],
            "lag_1": history_counts[-1],
            "lag_24": history_counts[-24] if len(history_counts) >= 24 else history_counts[-1],
            "lag_168": history_counts[-168] if len(history_counts) >= 168 else history_counts[-1],
            "rolling_24": sum(history_counts[-24:]) / min(24, len(history_counts)),
        }
        prediction = float(model.predict(pd.DataFrame([features], columns=feature_columns))[0])
        prediction = max(0.0, prediction)
        history_counts.append(prediction)
        output.at[index, "count"] = prediction

    return output[
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


def _naive_forecast(frame: pd.DataFrame, future_base: pd.DataFrame) -> pd.DataFrame:
    output = future_base.copy()
    hourly_profile = frame.groupby("hour")["count"].median().to_dict()
    overall_median = float(frame["count"].median())
    weekend_multiplier = {
        0: _safe_median(frame.loc[frame["is_weekend"] == 0, "count"], overall_median),
        1: _safe_median(frame.loc[frame["is_weekend"] == 1, "count"], overall_median),
    }
    baseline = max(1.0, weekend_multiplier[0])

    for index, row in output.iterrows():
        base = float(hourly_profile.get(int(row["hour"]), overall_median))
        weekend_factor = weekend_multiplier[int(row["is_weekend"])] / baseline
        output.at[index, "count"] = max(0.0, base * weekend_factor)

    return output[
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


def _safe_median(series: pd.Series, fallback: float) -> float:
    median = series.median()
    if pd.isna(median):
        return fallback
    return float(median)
