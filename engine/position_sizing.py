"""
position_sizing.py
Shared helper for deciding how many shares to buy, given a maximum
fraction of the portfolio to risk on a single trade. Used by every
strategy instead of each one duplicating this math separately.
"""



def calculate_shares(portfolio, price: float, position_size_pct: float = 1.0, commission: float = 1.0) -> int:
    """
        Returns the number of whole shares affordable within position_size_pct
        of the portfolio's TOTAL cash (not total value - keeps sizing simple
        and cash-based rather than needing current holdings' market value).
    
        position_size_pct: fraction of cash to risk on this trade (0.25 = 25%).
        Defaults to 1.0 (100%) to match the old all-in behavior if not specified.
    """

    max_spend = portfolio.cash * position_size_pct
    affordable = int((max_spend - commission) // price)

    return max(affordable, 0)

'''
Why portfolio.cash * position_size_pct and not portfolio.total_value(...)
* position_size_pct: total value would require passing in current prices 
for every held ticker just to size one trade, which adds complexity for a 
marginal difference in this project's scope. Sizing off available cash 
is a reasonable, simpler standard.
'''

