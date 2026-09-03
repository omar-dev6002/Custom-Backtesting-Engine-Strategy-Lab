"""
broker.py
Takes an Order and a current price, decides whether it can be filled,
and if so, applies it to the Portfolio. This is the only place that
touches both Order and Portfolio.
"""

from engine.portfolio import Portfolio
from engine.order import Order


class Broker:
    def __init__(self, portfolio: Portfolio, commission: float = 1.0):
        self.portfolio = portfolio
        self.commission = commission

    def execute(self, order: Order, fill_price: float):
        """
        Attempt to fill `order` at `fill_price`. Returns True if filled,
        False if rejected (insufficient cash or shares).
        """
        if order.side == "BUY":
            cost = order.quantity * fill_price + self.commission
            if cost > self.portfolio.cash:
                print(f"[broker] REJECTED: not enough cash for {order.quantity} {order.ticker} "
                      f"(need {cost:.2f}, have {self.portfolio.cash:.2f})")
                return False

        else:  # SELL
            held = self.portfolio.get_positions(order.ticker)
            if order.quantity > held:
                print(f"[broker] REJECTED: trying to sell {order.quantity} {order.ticker}, "
                      f"only hold {held}")
                return False

        self.portfolio.update_on_fill(
            ticker=order.ticker,
            quantity=order.quantity,
            side=order.side,
            fill_price=fill_price,
            commission=self.commission,
            date=order.date,
        )
        return True