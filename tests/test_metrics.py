"""
test_metrics.py
Unit tests for engine/metrics.py, checked against hand-calculated
examples from derivations.md. Run with: pytest
"""

from datetime import datetime, timedelta
import pytest
from engine.metrics import calculate_cagr, calculate_sharpe, calculate_sortino, calculate_max_drawdown


def make_equity_curve(values, start_date=datetime(2023, 1, 1)):
    """Helper: builds an equity_curve list from a plain list of portfolio values, one per day."""
    return [
        {"Date": start_date + timedelta(days=i), "Total Value": v}
        for i, v in enumerate(values)
    ]


def test_cagr_doubling_over_two_years():
    """From derivations.md Day 11: doubling $10,000 to $20,000 over 2 years should give ~41.4% CAGR."""
    curve = make_equity_curve([10000, 20000], start_date=datetime(2021, 1, 1))
    # force exactly 2 years by overriding the second date directly
    curve[1]["Date"] = datetime(2023, 1, 1)

    cagr = calculate_cagr(curve)
    assert cagr == pytest.approx(0.414, abs=0.01)


def test_sharpe_matches_hand_calculation():
    """From derivations.md Day 12: the 5-day +1%,-0.5%,+2%,+0.5%,-1% example gives Sharpe ~5.33."""
    values = [100, 101, 100.495, 102.50490, 103.0174245, 101.987250255]
    curve = make_equity_curve(values)

    sharpe = calculate_sharpe(curve)
    assert sharpe == pytest.approx(5.33, rel=0.02)


def test_sortino_matches_hand_calculation():
    """From derivations.md Day 13: same 5-day example gives Sortino ~12.70."""
    values = [100, 101, 100.495, 102.50490, 103.0174245, 101.987250255]
    curve = make_equity_curve(values)

    sortino = calculate_sortino(curve)
    assert sortino == pytest.approx(12.70, rel=0.02)


def test_max_drawdown_matches_hand_calculation():
    """From derivations.md Day 14: the 7-day example with a dip to $9,000 gives max drawdown ~-18.2%."""
    values = [10000, 10500, 11000, 9500, 9000, 10200, 12000]
    curve = make_equity_curve(values)

    drawdown = calculate_max_drawdown(curve)
    assert drawdown == pytest.approx(-0.182, abs=0.01)


def test_max_drawdown_is_zero_when_always_rising():
    """Edge case: a strategy that only ever goes up should have exactly 0 drawdown."""
    values = [10000, 10100, 10300, 10500, 11000]
    curve = make_equity_curve(values)

    drawdown = calculate_max_drawdown(curve)
    assert drawdown == 0.0