"""
buy_and_hold.py
Simplest possible baseline strategy: buy as many shares as affordable
on the first day, then never trade again. This is the benchmark every
other strategy should try to beat - if a fancier strategy can't outperform
just buying and holding, the added complexity isn't worth it.
"""


from engine.order import Order 

def generate_signal(date, price: float, ticker: str, portfolio, has_bought: bool):
    """
        Returns an Order, or None if no action this day.
        `has_bought` tracks whether we've already made our one purchase -
        the event loop passes this in and updates it based on our return value.
    """

    if has_bought:
        return None

    # buy as many whole shares as affordable, leaving $1 headroom for commission
    affordable_shares = int((portfolio.cash -1.0) // price)

    if affordable_shares <= 0:
        return None

    return Order(ticker = ticker, quantity = affordable_shares, side = "BUY", date = date)

