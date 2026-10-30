"""
test_lookahead.py
Truncation test for lookahead bias: if a strategy only uses information
available up to each day, cutting off the future must not change anything
that happened before the cut. Synthetic prices, so no network or cache needed.

Two checks: (1) indicator columns computed on truncated data must match the
same rows computed on the full data - this catches any peek ahead, even one
day, whether or not it happens to trigger a trade; (2) the full equity curve
must not change - end-to-end check through the real event loop.

What this does NOT catch: same-bar execution (deciding on today's close and
filling at today's close). That uses no future rows, so it passes here anyway.
"""

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from engine.backtester import run_backtest
from strategies import buy_and_hold, sma_crossover, rsi_strategy, momentum_breakout

TICKER = "TEST"
CUTS = [120, 160, 200, 240]  # several cut points, since a shift(-k) bug only shows up near the cut


def make_prices(n=300, seed=7):
    rng = np.random.default_rng(seed)
    returns = rng.normal(0.0005, 0.015, n)
    close = 100 * np.exp(np.cumsum(returns))
    dates = pd.bdate_range("2020-01-01", periods=n)
    return pd.DataFrame({"Close": close}, index=dates)


def values(curve):
    return [point["Total Value"] for point in curve]


STRATEGIES = {
    "buy_and_hold": (buy_and_hold.generate_signal, None),
    "sma_crossover": (sma_crossover.generate_signal, sma_crossover.prepare),
    "rsi": (rsi_strategy.generate_signal, rsi_strategy.prepare),
    "momentum_breakout": (momentum_breakout.generate_signal, momentum_breakout.prepare),
}


@pytest.mark.parametrize("name", STRATEGIES.keys())
@pytest.mark.parametrize("cut", CUTS)
def test_future_does_not_change_the_past(name, cut):
    strategy_fn, prepare_fn = STRATEGIES[name]
    prices = make_prices()

    full_curve, _ = run_backtest(prices, TICKER, strategy_fn, prepare_fn=prepare_fn)
    short_curve, _ = run_backtest(prices.iloc[:cut], TICKER, strategy_fn, prepare_fn=prepare_fn)

    assert values(short_curve) == values(full_curve)[:cut]


@pytest.mark.parametrize("name", [n for n, (_, prep) in STRATEGIES.items() if prep is not None])
@pytest.mark.parametrize("cut", CUTS)
def test_indicators_use_only_past_data(name, cut):
    prepare_fn = STRATEGIES[name][1]
    prices = make_prices()

    from_full = prepare_fn(prices).iloc[:cut]
    from_truncated = prepare_fn(prices.iloc[:cut])

    assert_frame_equal(from_truncated, from_full)


def leaky_breakout_prepare(price_data, window=20):
    """Breakout indicator with shift(-1) instead of shift(1): quietly looks one day ahead."""
    df = price_data.copy()
    df["Rolling_High"] = df["Close"].shift(-1).rolling(window).max()
    df["Rolling_Low"] = df["Close"].shift(-1).rolling(window).min()
    df["Buy_Signal"] = df["Close"] > df["Rolling_High"]
    df["Sell_Signal"] = df["Close"] < df["Rolling_Low"]
    return df


def test_indicator_check_catches_a_one_day_leak():
    """The equity-curve check misses this (only the last day before the cut is affected); this one must not."""
    prices = make_prices()
    cut = 200

    with pytest.raises(AssertionError):
        assert_frame_equal(leaky_breakout_prepare(prices.iloc[:cut]), leaky_breakout_prepare(prices).iloc[:cut])


def cheating_prepare(price_data):
    """Deliberately leaky: compares each price to the mean of the WHOLE series, future included."""
    df = price_data.copy()
    full_mean = df["Close"].mean()
    df["Buy_Signal"] = df["Close"] < full_mean
    df["Sell_Signal"] = df["Close"] > full_mean
    return df


def test_the_test_catches_a_cheating_strategy():
    """If this ever passes the truncation check, the check above has no teeth."""
    prices = make_prices()
    cut = 200

    full_curve, _ = run_backtest(prices, TICKER, rsi_strategy.generate_signal, prepare_fn=cheating_prepare)
    short_curve, short_pf = run_backtest(prices.iloc[:cut], TICKER, rsi_strategy.generate_signal, prepare_fn=cheating_prepare)

    assert len(short_pf.trade_log) > 0  # it has to actually trade for the comparison to mean anything
    assert values(short_curve) != values(full_curve)[:cut]