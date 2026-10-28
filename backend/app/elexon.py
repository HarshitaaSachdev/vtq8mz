"""Thin client for the two Elexon BMRS datasets we use."""
from datetime import date, datetime

import httpx

from .config import ELEXON_BASE_URL

TIMEOUT_SECONDS = 60


def fetch_wind_actuals(date_from: date, date_to: date) -> list[dict]:
    """Actual national wind generation (FUELHH), one row per 30-minute period."""
    response = httpx.get(
        f"{ELEXON_BASE_URL}/FUELHH/stream",
        params={
            "settlementDateFrom": date_from.isoformat(),
            "settlementDateTo": date_to.isoformat(),
            "fuelType": "WIND",
        },
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return [
        {"startTime": row["startTime"], "generation": row["generation"]}
        for row in response.json()
        if row["fuelType"] == "WIND"
    ]


def fetch_wind_forecasts(publish_from: datetime, publish_to: datetime) -> list[dict]:
    """Wind forecasts (WINDFOR). Each forecast run covers the next ~2 days, hourly."""
    response = httpx.get(
        f"{ELEXON_BASE_URL}/WINDFOR/stream",
        params={
            "publishDateTimeFrom": publish_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "publishDateTimeTo": publish_to.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return [
        {
            "startTime": row["startTime"],
            "publishTime": row["publishTime"],
            "generation": row["generation"],
        }
        for row in response.json()
    ]