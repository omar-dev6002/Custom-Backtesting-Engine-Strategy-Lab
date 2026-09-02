"""
portfolio.py
Tracks cash, current holdings, and trade history.
The Broker calls into this after every fill - Portfolio never decides
whether a trade happens, it just records the result.
"""


class Portfolio:
    def __init__(self, starting_cash: float):
        self.cash = starting_cash
        self.positions = {}         # {ticker: number of shares held}
        self.trade_log = []         # list of dicts, one per executed trade

    def update_on_fill(self, ticker: str, quantity: int, side: str, fill_price: float, commission: float, date):
        """
        Called by the Broker after a trade executes. Updates cash and
        positions, and appends a record to the trade log.
        """

        trade_value = quantity * fill_price

        if side == "BUY":
            self.cash -= (trade_value + commission)
            self.positions[ticker] = self.positions.get(ticker, 0) + quantity

        else:
            self.cash += (trade_value - commission)
            self.positions[ticker] = self.positions.get(ticker, 0) - quantity


        self.trade_log.append({
            "Date": date,
            "Ticker": ticker,
            "Side": side,
            "Quantity": quantity,
            "Fill price": fill_price,
            "Commission": commission,
            "Cash after": self.cash,
        })

    def get_positions(self, ticker: str) -> int:
        """How many shares of `ticker` we currently hold. 0 if none."""
        return self.positions.get(ticker, 0)

    def total_value(self, current_prices: dict) -> float:
        """
        Cash + market value of all holdings, given a dict of
        {ticker: current_price}. This is what your equity curve tracks
        over time in Week 3.
        """

        holdings_value = sum(
            shares * current_prices[ticker]
            for ticker, shares in self.positions.items()
            if shares != 0
        )
        
        return self.cash + holdings_value





