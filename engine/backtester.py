"""
backtester.py
The event loop: replays price data day by day, asks the strategy for a
decision, sends any resulting order to the Broker, and records portfolio
value each day. That daily value series is the equity curve.

If the strategy needs indicators (moving averages, RSI, etc.), pass a
prepare_fn that adds those columns to price_data before the loop starts.
Because indicators are computed with pandas rolling operations, each row's
value only ever depends on past rows - no lookahead risk from doing this
upfront instead of day-by-day.
"""


import pandas as pd
from engine.portfolio import Portfolio
from engine.broker import Broker


def run_backtest(price_data: pd.DataFrame, ticker : str, strategy_fn, prepare_fn = None ,starting_cash: float = 10000, commission: float = 1.0, slippage_pct: float = 0.0):
    """
        price_data: DataFrame with a 'Close' column, indexed by date.
        strategy_fn: function(date, price, ticker, portfolio, has_bought) -> Order or None
        prepare_fn: optional function(price_data) -> price_data with extra
            indicator columns added (e.g. SMA_fast, SMA_slow).
        
        Returns (equity_curve, portfolio) - equity_curve is a list of {date, total_value} dicts, one per day.
    """

    if prepare_fn is not None:
        price_data = prepare_fn(price_data)

    portfolio = Portfolio(starting_cash = starting_cash)
    broker = Broker(portfolio = portfolio, commission = commission, slippage_pct= slippage_pct)

    equity_curve = []
    

    for date, row in price_data.iterrows():
        price = row['Close']

        order  = strategy_fn(date, row, ticker, portfolio)

        if order is not None:
            broker.execute(order, quoted_price = price)

        total_value = portfolio.total_value(current_prices = {ticker: price})
        equity_curve.append({"Date": date, "Total Value": total_value})

    return equity_curve, portfolio

'''
prepare_fn parameter (runs once, before the loop, to add indicator columns),
and strategy_fn now receives the full row instead of just price — same price
= row["Close"] line still exists internally for the Broker fill, unchanged 
from before.

'''


    