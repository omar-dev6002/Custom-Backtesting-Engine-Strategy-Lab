"""
test_strategies.py
Pins strategy parameters and basic behaviour. Added after the SMA default
silently became slow_window=10 and every SMA result was wrong.
"""

import numpy as np
import pandas as pd
import pytest

from strategies import sma_crossover


def make_prices(n=150, seed=3):
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.015, n)))
    return pd.DataFrame({"Close": close}, index=pd.bdate_range("2020-01-01", periods=n))


def test_sma_default_windows_are_20_and_50():
    df = sma_crossover.prepare(make_prices())

    assert df["SMA_fast"].first_valid_index() == df.index[19]   # 20th day
    assert df["SMA_slow"].first_valid_index() == df.index[49]   # 50th day


def test_sma_cannot_signal_before_the_slow_average_exists():
    early = sma_crossover.prepare(make_prices()).iloc[:49]

    assert not early["Cross_Up"].any()
    assert not early["Cross_Down"].any()


def test_sma_rejects_a_fast_window_that_is_not_smaller():
    with pytest.raises(ValueError):
        sma_crossover.prepare(make_prices(), fast_window=20, slow_window=10)


from strategies import rsi_strategy, momentum_breakout


def test_rsi_default_period_and_thresholds():
    import inspect
    defaults = inspect.signature(rsi_strategy.prepare).parameters
    assert defaults["period"].default == 14
    assert defaults["oversold"].default == 30
    assert defaults["overbought"].default == 70


def test_momentum_default_window():
    import inspect
    defaults = inspect.signature(momentum_breakout.prepare).parameters
    assert defaults["window"].default == 20