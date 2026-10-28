from datetime import date, datetime, time, timezone

from app.data import build_dataset
from app.forecasts import build_series, decision_cutoff, horizon_cutoff, latest_forecast_before, target_times


def utc(day, hour, minute=0):
    return datetime(2026, 1, day, hour, minute, tzinfo=timezone.utc)


def make_dataset():
    target = "2026-01-10T12:00:00Z"
    return build_dataset(
        actual_rows=[{"startTime": target, "generation": 10000}],
        forecast_rows=[
            {"startTime": target, "publishTime": "2026-01-08T22:30:00Z", "generation": 8000},
            {"startTime": target, "publishTime": "2026-01-09T07:30:00Z", "generation": 9000},
            {"startTime": target, "publishTime": "2026-01-09T09:30:00Z", "generation": 9500},
            # Published after the target time -> not a real forecast, must be ignored
            {"startTime": target, "publishTime": "2026-01-10T13:30:00Z", "generation": 10000},
        ],
    )


def test_picks_latest_forecast_published_before_cutoff():
    candidates = make_dataset().forecasts[utc(10, 12)]
    chosen = latest_forecast_before(candidates, utc(9, 9))
    assert chosen.generation == 9000


def test_never_uses_a_forecast_published_after_cutoff():
    candidates = make_dataset().forecasts[utc(10, 12)]
    assert latest_forecast_before(candidates, utc(8, 0)) is None


def test_forecasts_published_after_target_are_dropped():
    assert len(make_dataset().forecasts[utc(10, 12)]) == 3


def test_decision_cutoff_is_day_before_delivery_in_uk_time():
    cutoff = decision_cutoff(time(9, 0))
    assert cutoff(utc(10, 12)) == utc(9, 9)
    # In summer UK time is BST (UTC+1), so 09:00 UK is 08:00 UTC
    summer_target = datetime(2026, 7, 10, 12, tzinfo=timezone.utc)
    assert cutoff(summer_target) == datetime(2026, 7, 9, 8, tzinfo=timezone.utc)


def test_horizon_cutoff_subtracts_hours():
    assert horizon_cutoff(24)(utc(10, 12)) == utc(9, 12)


def test_target_times_cover_full_days_in_half_hours():
    times = target_times(date(2026, 1, 10), date(2026, 1, 11))
    assert len(times) == 96
    assert times[0] == utc(10, 0) and times[-1] == utc(11, 23, 30)


def test_build_series_reports_chosen_forecast_and_horizon():
    [point] = build_series(make_dataset(), [utc(10, 12)], decision_cutoff(time(9, 0)))
    assert (point.actual, point.forecast) == (10000, 9000)
    assert point.horizon_hours == 28.5