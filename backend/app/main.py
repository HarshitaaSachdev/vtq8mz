"""HTTP API consumed by the React frontend. All routes live under /api."""
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import DEFAULT_DECISION_TIME, FIRST_DELIVERY_DAY, LAST_DELIVERY_DAY, MAX_HORIZON_HOURS
from .data import Dataset, load_dataset
from .forecasts import Point, build_series, decision_cutoff, horizon_cutoff, target_times
from .metrics import Metrics, compute_metrics

app = FastAPI(
    title="Wind Forecast Monitor API",
    version="1.0.0",
    # Under /api so the docs are routed to the backend on Vercel too
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

DEFAULT_HORIZONS = [0, 1, 2, 4, 6, 8, 12, 16, 20, 24, 30, 36, 42, 48]


@dataclass
class Meta:
    first_delivery_day: date
    last_delivery_day: date
    default_decision_time: time
    max_horizon_hours: int
    actual_points: int
    forecast_runs: int


@dataclass
class SeriesResponse:
    points: list[Point]
    metrics: Metrics | None


@dataclass
class HorizonAccuracy:
    horizon_hours: float
    metrics: Metrics | None


def get_dataset() -> Dataset:
    # Wrapped in a dependency so tests can swap in a small fake dataset.
    return load_dataset()


def validate_range(start: date | None, end: date | None) -> tuple[date, date]:
    start = start or FIRST_DELIVERY_DAY
    end = end or LAST_DELIVERY_DAY
    if start > end:
        raise HTTPException(422, "start must be on or before end")
    if start < FIRST_DELIVERY_DAY or end > LAST_DELIVERY_DAY:
        raise HTTPException(422, f"dates must be within {FIRST_DELIVERY_DAY} .. {LAST_DELIVERY_DAY}")
    return start, end


def metrics_for(points: list[Point]) -> Metrics | None:
    return compute_metrics([
        (p.forecast, p.actual) for p in points if p.forecast is not None and p.actual is not None
    ])


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/meta")
def meta(dataset: Dataset = Depends(get_dataset)) -> Meta:
    publish_times = {f.publish_time for runs in dataset.forecasts.values() for f in runs}
    return Meta(
        first_delivery_day=FIRST_DELIVERY_DAY,
        last_delivery_day=LAST_DELIVERY_DAY,
        default_decision_time=DEFAULT_DECISION_TIME,
        max_horizon_hours=MAX_HORIZON_HOURS,
        actual_points=len(dataset.actuals),
        forecast_runs=len(publish_times),
    )


@app.get("/api/series")
def series(
    mode: Literal["decision", "horizon"] = "decision",
    decision_time: time = DEFAULT_DECISION_TIME,
    horizon_hours: float = Query(24, ge=0, le=MAX_HORIZON_HOURS),
    start: date | None = None,
    end: date | None = None,
    dataset: Dataset = Depends(get_dataset),
) -> SeriesResponse:
    """Actual vs forecast for each 30-min period, plus error metrics for the range."""
    start, end = validate_range(start, end)
    cutoff_fn = decision_cutoff(decision_time) if mode == "decision" else horizon_cutoff(horizon_hours)
    points = build_series(dataset, target_times(start, end), cutoff_fn)
    return SeriesResponse(points=points, metrics=metrics_for(points))


@app.get("/api/accuracy/by-horizon")
def accuracy_by_horizon(
    start: date | None = None,
    end: date | None = None,
    dataset: Dataset = Depends(get_dataset),
) -> list[HorizonAccuracy]:
    """How forecast error grows the further ahead the forecast was made."""
    start, end = validate_range(start, end)
    targets = target_times(start, end)
    return [
        HorizonAccuracy(h, metrics_for(build_series(dataset, targets, horizon_cutoff(h))))
        for h in DEFAULT_HORIZONS
    ]