import pytest

from app.metrics import compute_metrics, percentile


def test_percentile_matches_linear_interpolation():
    assert percentile([1, 2, 3, 4], 50) == 2.5
    assert percentile([10], 90) == 10


def test_metrics_on_known_values():
    # errors (forecast - actual): +100, -100, +200, 0
    m = compute_metrics([(1100, 1000), (900, 1000), (1200, 1000), (1000, 1000)])
    assert m.count == 4
    assert m.mae == 100
    assert m.bias == 50
    assert m.rmse == pytest.approx(122.5, abs=0.1)
    assert m.nmae_pct == 10
    assert m.max_shortfall == 200


def test_metrics_empty_returns_none():
    assert compute_metrics([]) is None