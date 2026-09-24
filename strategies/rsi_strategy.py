"""
rsi_strategy.py
Mean-reversion strategy using RSI. Buys when RSI drops below the oversold
threshold (price fell hard/fast, betting on a bounce), sells when RSI
rises above the overbought threshold (price rose hard/fast, betting on
a pullback).

Note: this uses a simple rolling average for gains/losses. The "textbook"
RSI (Wilder's RSI) uses an exponential smoothing instead, which behaves
slightly differently. Worth knowing this is a simplification, not the
only correct way to compute it.
"""
from engine.position_sizing import calculate_shares
from engine.order import Order


def prepare(price_data, period: int = 14, oversold: float = 30, overbought: float = 70):
    """
        Adds an RSI column to price_data, computed over a rolling `period`-day
        window. Also adds precomputed Buy_Signal/Sell_Signal boolean columns.
    """
    df = price_data.copy()

    delta = df['Close'].diff()

    gain = delta.clip(lower = 0)
    loss = -delta.clip(upper = 0)


    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss 
    df['RSI'] = 100 - (100 / (1 + rs))

    df["Buy_Signal"] = df["RSI"] < oversold
    df["Sell_Signal"] = df["RSI"] > overbought

    return df


def generate_signal(date, row, ticker: str, portfolio):
    """
        Buy when oversold and not already holding. Sell everything when
        overbought and currently holding.
    """

    held = portfolio.get_positions(ticker)

    if row["Buy_Signal"] and held == 0:
        price = row["Close"]
        affordable_shares = calculate_shares(portfolio, price, position_size_pct= 0.25 )

        if affordable_shares <= 0:
            return None

        return Order(ticker= ticker, quantity= affordable_shares, side="BUY", date= date)

    if row["Sell_Signal"] and held > 0:
        return Order(ticker= ticker, quantity= held, side= "SELL", date= date)

    return None

