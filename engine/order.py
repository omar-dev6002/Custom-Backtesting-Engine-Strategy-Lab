"""
order.py
Represents a single trade instruction. Just data — no execution logic here.
The Broker is what actually decides if/how this gets filled.
"""
from dataclasses import dataclass
from datetime import datetime

@dataclass

class Order:
    ticker : str
    quantity : int                    # always positive - side tells us buy vs sell
    side : str                        # "BUY" or "SELL"
    date : datetime                   # the day this order was placed

    def __post_init__(self):
        # dataclasses run __init__ automatically from the fields above,
        # but __post_init__ lets us add validation after that happens
        if self.side not in ("BUY", "SELL"):
            raise ValueError((f"side must be'BUY' or 'SELL', got '{self.side}'"))

        if self.quantity <= 0:
            raise ValueError(f"Quantity must be (+)ve, got {self.quantity} ")

