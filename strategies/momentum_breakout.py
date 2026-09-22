"""
momentum_breakout.py
Momentum strategy: buy when price breaks above its recent N-day high
(a genuinely new extreme, not just a moving-average crossing), sell
when it breaks below its recent N-day low.

Uses .shift(1) on the rolling high/low so today's price is compared
against the PRIOR N days only - not a window that includes today,
which would make a real breakout impossible to detect (today's price
can't be "above" a high that already includes today's own value).
"""

from engine.order import Order


def prepare(price_data, window: int = 20):
    """
        Adds Rolling_High, Rolling_Low, and precomputed Buy/Sell signal
        columns to price_data.
    """

    df = price_data.copy()

    df['Rolling_High'] = df["Close"].shift(1).rolling(window).max()
    df['Rolling_Low'] = df["Close"].shift(1).rolling(window).min()

    df["Buy_Signal"] = df["Close"] > df["Rolling_High"]
    df["Sell_Signal"] = df["Close"] < df["Rolling_Low"]

    return df


def generate_signal(date, row, ticker: str, portfolio):
    """
    Buy on a breakout above the recent high if not already holding.
    Sell everything on a breakdown below the recent low if currently holding.
    """

    held = portfolio.get_positions(ticker)

    if row["Buy_Signal"] and held == 0:
        price = row["Close"]
        affordable_shares = int((portfolio.cash - 1.0) // price)
        if affordable_shares <= 0:
            return None
        return Order(ticker= ticker, quantity= affordable_shares, side= "BUY", date= date)

    if row["Sell_Signal"] and held > 0:
        return Order(ticker= ticker, quantity= held, side= "SELL", date= date)


    return None

'''
df["Close"].shift(1).rolling(window).max() — read right-to-left in execution
order: first .shift(1) moves the whole Close column down by one row (so 
"today's" slot now holds yesterday's price), then .rolling(window).max() 
computes the rolling max on that shifted series.
'''