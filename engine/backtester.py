"""
backtester.py
The event loop: replays price data day by day, asks the strategy for a
decision, sends any resulting order to the Broker, and records portfolio
value each day. That daily value series is the equity curve.
"""


import pandas as pd
from engine.portfolio import Portfolio
from engine.broker import Broker


def run_backtest(price_data: pd.DataFrame, ticker : str, strategy_fn, starting_cash: float = 10000, commission: float = 1.0):
    """
        price_data: DataFrame with a 'Close' column, indexed by date.
        strategy_fn: function(date, price, ticker, portfolio, has_bought) -> Order or None
    
        Returns (equity_curve, portfolio) - equity_curve is a list of
        {date, total_value} dicts, one per day.
    """
    portfolio = Portfolio(starting_cash = starting_cash)
    broker = Broker(portfolio = portfolio, commission = commission)

    equity_curve = []
    has_bought = False

    for date, row in price_data.iterrows():
        price = row['Close']

        order  = strategy_fn(date, price, ticker, portfolio, has_bought)

        if order is not None:
            filled = broker.execute(order, fill_price = price)
            if filled and order.side == "BUY":
                has_bought = True

        total_value = portfolio.total_value(current_prices = {ticker: price})
        equity_curve.append({"Date": date, "Total Value": total_value})

    return equity_curve, portfolio



    