"""
walk_forward.py
Runs each strategy on multiple, separate yearly windows instead of one
continuous backtest - testing whether results hold up across different
market regimes, not just the single year already tested.

IMPORTANT LIMITATION: each window is treated independently. A strategy
like SMA Crossover needs 50 days of price history before its slow SMA
has a real value, so the first ~50 days of EVERY window can't generate
signals - there's no "carrying over" indicator history from the prior
year. This slightly understates how each strategy would perform in a
continuous multi-year backtest, and is worth being upfront about rather
than hiding.
"""

import pandas as pd
from engine.backtester import run_backtest
from engine.metrics import calculate_max_drawdown, calculate_cagr, calculate_sharpe, calculate_sortino


def split_by_year(price_data: pd.DataFrame) -> dict:
    """Splits price_data into separate DataFrames, one per calendar year."""
    windows = {}
    for year, group in price_data.groupby(price_data.index.year):
        windows[year] = group

    return windows

def run_walk_forward(price_data: pd.DataFrame, ticker: str, strategies: dict, starting_cash: float = 10000, commission: float = 1.0, slippage_pct: float = 0.001):
    """
        strategies: {name: (strategy_fn, prepare_fn)} - prepare_fn can be None.
        Runs every strategy on every yearly window independently - each window
        starts fresh with starting_cash, windows are NOT chained together.
    
        Returns a list of result dicts, one per (strategy, year) combination.
    """

    windows = split_by_year(price_data)
    results = []

    for year, window_data in windows.items():
        for strategy_name , (strategy_fn, prepare_fn) in strategies.items():
            equity_curve, portfolio = run_backtest(
                price_data= window_data,
                ticker= ticker,
                strategy_fn= strategy_fn,
                prepare_fn= prepare_fn,
                starting_cash= starting_cash,
                commission= commission,
                slippage_pct= slippage_pct,
            )

            results.append({
                "Year" : year,
                "Strategy" : strategy_name,
                "CAGR" : calculate_cagr(equity_curve),
                "Sharpe" : calculate_sharpe(equity_curve),
                "Sortino": calculate_sortino(equity_curve),
                "Max Drawdown" : calculate_max_drawdown(equity_curve),
                "Trades" : len(portfolio.trade_log)
            })
    return results

    