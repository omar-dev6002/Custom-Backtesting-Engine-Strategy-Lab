"""
metrics.py
Risk/return metrics computed from an equity curve. Everything here reads
the same equity_curve format produced by run_backtest() - a list of
{"Date": ..., "Total Value": ...} dicts, one per day.
"""


import pandas as pd


def to_return_series(equity_curve) -> pd.Series:
    """
        Converts the equity curve into a pandas Series of DAILY returns
        (as decimals, e.g. 0.015 = 1.5%). This is the shared building block
        every other metric in this file is computed from.
    """

    df = pd.DataFrame(equity_curve).set_index("Date")
    daily_returns = df["Total Value"].pct_change
    return daily_returns.dropna()


def calculate_cagr(equity_curve) -> float:
    """
        Compound Annual Growth Rate: the constant yearly growth rate that
        would produce the same total return over the actual time period.
    """
    df = pd.DataFrame(equity_curve).set_index("Date")

    start_value = df["Total Value"].iloc[0]
    end_value = df["Total Value"].iloc[-1]

    start_date = df.index[0]
    end_date = df.index[-1]

    years = (end_date - start_date).days / 365.25

    if years <= 0 or start_value <= 0:
        return 0.0

    return (end_value / start_value) ** (1 / years) - 1


