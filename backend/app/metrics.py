"""Forecast error statistics.

Sign convention: error = forecast - actual.
A positive error means wind came in BELOW forecast, i.e. the buyer is short
of power and must buy the gap at short notice. That is the costly direction.
"""
import math
from dataclasses import dataclass


@dataclass
class Metrics:
    count: int              # number of hours compared
    mean_actual: float      # average actual wind (MW), for scale
    mae: float              # mean absolute error (MW)
    nmae_pct: float         # MAE as a % of average actual generation
    rmse: float             # root mean squared error (MW), punishes big misses
    bias: float             # mean error (MW): >0 means forecasts are too optimistic
    p50_abs_error: float    # half of all hours had an error smaller than this
    p90_abs_error: float    # 90% of hours had an error smaller than this
    p90_shortfall: float    # in 90% of hours, actual >= forecast - this (a reserve margin)
    max_shortfall: float    # worst single hour where wind fell below forecast


def percentile(values: list[float], q: float) -> float:
    """Linear-interpolated percentile, q in [0, 100] (same method as numpy's default)."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * q / 100
    lower, upper = math.floor(position), math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def compute_metrics(pairs: list[tuple[float, float]]) -> Metrics | None:
    """`pairs` is a list of (forecast, actual). Returns None if there is nothing to compare."""
    if not pairs:
        return None
    errors = [forecast - actual for forecast, actual in pairs]
    abs_errors = [abs(e) for e in errors]
    mean_actual = sum(actual for _, actual in pairs) / len(pairs)
    mae = sum(abs_errors) / len(errors)
    return Metrics(
        count=len(errors),
        mean_actual=round(mean_actual, 1),
        mae=round(mae, 1),
        nmae_pct=round(100 * mae / mean_actual, 1) if mean_actual else 0.0,
        rmse=round(math.sqrt(sum(e * e for e in errors) / len(errors)), 1),
        bias=round(sum(errors) / len(errors), 1),
        p50_abs_error=round(percentile(abs_errors, 50), 1),
        p90_abs_error=round(percentile(abs_errors, 90), 1),
        p90_shortfall=round(max(percentile(errors, 90), 0.0), 1),
        max_shortfall=round(max(max(errors), 0.0), 1),
    )