"""
broker.py
Takes an Order and a current price, decides whether it can be filled,
and if so, applies it to the Portfolio. This is the only place that
touches both Order and Portfolio.

Models slippage: the price you actually get is slightly worse than the
quoted price - higher on a buy, lower on a sell - simulating the real
cost of your own order moving the price against you.
"""


from engine.portfolio import Portfolio
from engine.order import Order


class Broker:
    def __init__(self, portfolio: Portfolio, commission: float = 1.0, slippage_pct: float = 0.0):
        self.portfolio = portfolio
        self.commission = commission
        self.slippage_pct = slippage_pct 

    def _apply_slippage(self, quoted_price: float, side: str) -> float:
        """Returns the actual fill price after slippage - worse than quoted, in the direction that hurts us."""

        if side == "BUY":
            return quoted_price * (1 + self.slippage_pct)

        else:
            return quoted_price * (1 - self.slippage_pct)

    def execute(self, order: Order, quoted_price: float):
        """
            Attempt to fill `order`. `quoted_price` is the day's close (before
            slippage) - the actual fill price is computed internally. Returns
            True if filled, False if rejected.
        """
        
        fill_price = self._apply_slippage(quoted_price, order.side)

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