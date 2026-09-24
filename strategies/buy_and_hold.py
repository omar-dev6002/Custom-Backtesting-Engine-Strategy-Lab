"""
buy_and_hold.py
Simplest possible baseline strategy: buy as many shares as affordable
on the first day, then never trade again. This is the benchmark every
other strategy should try to beat - if a fancier strategy can't outperform
just buying and holding, the added complexity isn't worth it.
"""

from engine.position_sizing import calculate_shares
from engine.order import Order 

def generate_signal(date, row, ticker: str, portfolio):
    """
        Returns an Order, or None if no action this day.
        Checks the portfolio directly to see if we already hold a position,
        instead of tracking a separate flag - the portfolio is the single
        source of truth for what we own.
    """
    if portfolio.get_positions(ticker) > 0:
        return None  # already bought, do nothing

    price = row['Close']

    affordable_shares = calculate_shares(portfolio, price, position_size_pct= 0.25 )

    if affordable_shares <= 0:
        return None

    return Order(ticker = ticker, quantity = affordable_shares, side = "BUY", date = date)

'''
has_bought parameter is gone, replaced by directly checking
portfolio.get_positions(ticker) > 0. 
'''