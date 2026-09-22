"""
sma_crossover.py
Classic trend-following strategy: track a fast and slow moving average.
Buy when the fast average crosses above the slow one (uptrend starting),
sell when it crosses back below (uptrend fading).
"""


from engine.order import Order


def prepare(price_data, fast_window: int = 20, slow_window: int = 10):
    """
     Adds SMA_fast, SMA_slow, and precomputed crossover signal columns
     to price_data. Called once before the backtest loop starts.
    """  

    df = price_data.copy()

    df['SMA_fast'] = df['Close'].rolling(fast_window).mean()
    df['SMA_slow'] = df['Close'].rolling(slow_window).mean()

    diff = df['SMA_fast'] - df['SMA_slow']
    prev_diff = diff.shift(1)

    df['Cross_Up'] = (diff > 0) & (prev_diff <= 0)
    df['Cross_Down'] = (diff < 0) & (prev_diff >= 0)

    return df


def generate_signal(date, row, ticker: str, portfolio):
    """
        Buy on a crossover up if we don't already hold a position.
        Sell everything on a crossover down if we do.
    """

    held = portfolio.get_positions(ticker) 

    if row['Cross_Up'] and held == 0:
        price = row['Close']
        affordable_shares = int((portfolio.cash - 1.0) // price)
        if affordable_shares <= 0:
            return None
        return Order(ticker= ticker, quantity= affordable_shares, side = "BUY",date = date )


    if row['Cross_Down'] and held > 0:
        return Order(ticker= ticker, quantity= held, side = 'SELL', date = date)

    return None




   