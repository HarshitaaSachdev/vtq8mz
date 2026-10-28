"""Picks which forecast was 'the latest available' for each target time.

The golden rule: for a given cutoff, we may only use forecasts published at or
before that cutoff. Using a later forecast would be looking into the future.
"""
from bisect import bisect_right
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Callable

from .config import UK_TZ
from .data import Dataset, Forecast

CutoffFn = Callable[[datetime], datetime]


@dataclass
class Point:
    time: datetime
    actual: int | None
    forecast: int | None
    publish_time: datetime | None
    horizon_hours: float | None  # how far ahead the chosen forecast was made


def latest_forecast_before(candidates: list[Forecast], cutoff: datetime) -> Forecast | None:
    """Latest forecast published at or before `cutoff`. `candidates` must be sorted by publish_time."""
    index = bisect_right(candidates, cutoff, key=lambda f: f.publish_time)
    return candidates[index - 1] if index > 0 else None


def decision_cutoff(decision_time: time) -> CutoffFn:
    """Day-ahead view: forecasts known at `decision_time` (UK) on the day before delivery."""
    def cutoff(target: datetime) -> datetime:
        delivery_day = target.astimezone(UK_TZ).date()
        decision_day = delivery_day - timedelta(days=1)
        return datetime.combine(decision_day, decision_time, tzinfo=UK_TZ).astimezone(timezone.utc)
    return cutoff


def horizon_cutoff(horizon_hours: float) -> CutoffFn:
    """Fixed-horizon view: forecasts published at least `horizon_hours` before the target."""
    def cutoff(target: datetime) -> datetime:
        return target - timedelta(hours=horizon_hours)
    return cutoff


def target_times(first_day: date, last_day: date) -> list[datetime]:
    """Every 30-minute period (in UTC) covering the given UK delivery days."""
    start = datetime.combine(first_day, time(0), tzinfo=UK_TZ).astimezone(timezone.utc)
    end = datetime.combine(last_day + timedelta(days=1), time(0), tzinfo=UK_TZ).astimezone(timezone.utc)
    times = []
    current = start
    while current < end:
        times.append(current)
        current += timedelta(minutes=30)
    return times


def build_series(dataset: Dataset, targets: list[datetime], cutoff_fn: CutoffFn) -> list[Point]:
    points = []
    for target in targets:
        chosen = latest_forecast_before(dataset.forecasts.get(target, []), cutoff_fn(target))
        points.append(Point(
            time=target,
            actual=dataset.actuals.get(target),
            # Forecasts are hourly, so half-past points only carry an actual value.
            forecast=chosen.generation if chosen else None,
            publish_time=chosen.publish_time if chosen else None,
            horizon_hours=(target - chosen.publish_time).total_seconds() / 3600 if chosen else None,
        ))
    return points