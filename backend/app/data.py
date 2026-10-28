"""Loads the January 2026 dataset into memory.

The data is historical and never changes, so we keep a snapshot in data/*.json
(created by scripts/snapshot.py). If the snapshot is missing we fall back to
downloading it live from Elexon. Either way it is loaded once and cached.
"""
import json
from bisect import insort
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta, timezone
from functools import lru_cache
from pathlib import Path

from . import elexon
from .config import FIRST_DELIVERY_DAY, LAST_DELIVERY_DAY, MAX_HORIZON_HOURS, UK_TZ

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ACTUALS_FILE = DATA_DIR / "actuals.json"
FORECASTS_FILE = DATA_DIR / "forecasts.json"


@dataclass(frozen=True)
class Forecast:
    start_time: datetime    # the time being forecast (target time)
    publish_time: datetime  # when the forecast was created
    generation: int         # forecast wind generation in MW


@dataclass
class Dataset:
    # target time -> actual MW
    actuals: dict[datetime, int]
    # target time -> all forecasts for that time, sorted by publish_time (oldest first)
    forecasts: dict[datetime, list[Forecast]] = field(default_factory=dict)


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_dataset(actual_rows: list[dict], forecast_rows: list[dict]) -> Dataset:
    actuals = {parse_time(r["startTime"]): r["generation"] for r in actual_rows}

    forecasts: dict[datetime, list[Forecast]] = defaultdict(list)
    for row in forecast_rows:
        forecast = Forecast(
            start_time=parse_time(row["startTime"]),
            publish_time=parse_time(row["publishTime"]),
            generation=row["generation"],
        )
        # Elexon also republishes values for hours that have already passed.
        # Those are not forecasts any more, so we drop them.
        if forecast.publish_time > forecast.start_time:
            continue
        insort(forecasts[forecast.start_time], forecast, key=lambda f: f.publish_time)

    return Dataset(actuals=actuals, forecasts=dict(forecasts))


def download_window() -> tuple[tuple, tuple]:
    """The date ranges we need from Elexon to cover every delivery day and horizon."""
    first_target = datetime.combine(FIRST_DELIVERY_DAY, time(0), tzinfo=UK_TZ)
    last_target = datetime.combine(LAST_DELIVERY_DAY, time(23, 30), tzinfo=UK_TZ)
    actuals_range = (FIRST_DELIVERY_DAY - timedelta(days=1), LAST_DELIVERY_DAY)
    forecasts_range = (
        (first_target - timedelta(hours=MAX_HORIZON_HOURS)).astimezone(timezone.utc),
        last_target.astimezone(timezone.utc),
    )
    return actuals_range, forecasts_range


def fetch_raw_rows() -> tuple[list[dict], list[dict]]:
    actuals_range, forecasts_range = download_window()
    return elexon.fetch_wind_actuals(*actuals_range), elexon.fetch_wind_forecasts(*forecasts_range)


@lru_cache(maxsize=1)
def load_dataset() -> Dataset:
    if ACTUALS_FILE.exists() and FORECASTS_FILE.exists():
        actual_rows = json.loads(ACTUALS_FILE.read_text())
        forecast_rows = json.loads(FORECASTS_FILE.read_text())
    else:
        actual_rows, forecast_rows = fetch_raw_rows()
    return build_dataset(actual_rows, forecast_rows)