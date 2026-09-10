# Custom Backtesting Engine & Strategy Lab

A backtesting engine built from scratch in Python — no `backtrader`, no `zipline`, no `bt`. The point isn't to reinvent those libraries, it's to actually understand what a backtester is doing under the hood: order execution, position tracking, and (eventually) the risk metrics everyone quotes without knowing how they're computed.

This is part of a 5-project, 5-month portfolio. Project 1 was a neural network from scratch; this one moves into quant finance.

## Status

Week 1 complete. Full engine core built, tested, and producing a working backtest with a plotted equity curve. Week 2 (real strategies beyond buy-and-hold) is next.

## Results so far

Buy-and-hold, AAPL, 2023, $10,000 starting cash:

![Equity curve](equity_curve.png)

- Final value: **$15,453.07** (+54.5%)
- 1 trade (the initial buy — buy-and-hold never sells)
- The curve tracks AAPL's actual 2023 price action: steady climb into July, the August dip, recovery into September, a pullback into November, then a year-end rally. Not smoothed or fabricated — this is what actually happened.

## What's built so far

- **`engine/data_loader.py`** — pulls daily OHLCV data via `yfinance`, caches it locally as CSV so I'm not hitting the API on every run. Handles the MultiIndex column format yfinance returns by default (flattens it to plain `Close/High/Low/Open/Volume` columns).
- **`engine/order.py`** — represents a single trade instruction (ticker, quantity, side, date). A `dataclass` with validation in `__post_init__` — rejects bad sides (must be `BUY`/`SELL`) and non-positive quantities immediately instead of letting the bug surface downstream.
- **`engine/portfolio.py`** — tracks cash, current holdings (a `{ticker: shares}` dict), and a full trade log. `update_on_fill()` is called by the Broker after every trade. `total_value()` computes cash + market value of holdings, called every day of the backtest to build the equity curve.
- **`engine/broker.py`** — the middleman between Order and Portfolio. Checks whether a trade is actually possible (enough cash to buy, enough shares to sell) before applying it. Rejects invalid orders instead of silently going negative.
- **`engine/backtester.py`** — the event loop. Walks price data day by day, in order, asking the strategy for a decision using only that day's price (no lookahead into future data), routing any resulting order through the Broker, and recording portfolio value every day.
- **`strategies/buy_and_hold.py`** — first strategy: buys as many whole shares as affordable on day one, then holds. Deliberately simple — it's the baseline every more complex strategy in Week 2 needs to actually beat, not just match.

Bugs hit and fixed along the way: a type-hint typo (`starting_cash, float` instead of `starting_cash: float`); a stray `from matplotlib import ticker` autocomplete import masking a misspelled loop variable; a file that silently saved as 0 bytes in VS Code; a mistyped keyword argument (`curent_prices`); and a dict key naming mismatch between where the equity curve was built and where it was read. All of these were caught by actually running the code and checking the numbers against hand calculations, not by assuming it worked.

## Tickers

Starting with SPY, AAPL, MSFT, GOOGL, JPM — a mix of index ETF, tech megacaps, and financials, so I'm not just testing "does this work when tech goes up." All five are liquid enough that if a result looks weird, I can sanity-check it against any finance site.

## Setup

```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
python main.py
```

## Notes and derivations

`derivations.md` has photographed handwritten notes (finance terms, hand-worked calculations, the event loop design) paired with typed explanations, day by day. Working things out on paper before coding them has been the main way I'm avoiding just pattern-matching syntax without understanding what it represents financially.

## Why build the engine instead of using a library

Most student "algo trading" projects call `backtrader` or `zipline`, plot one equity curve, and call it done. That tests whether you can read documentation, not whether you understand what's happening between a signal and a filled trade — slippage, commissions, position sizing, what happens when you try to sell something you don't hold. Building it myself means I have to make those decisions explicitly instead of inheriting someone else's defaults.

## Known limitations (will grow as the project does)

- No slippage modeling, only a flat per-trade commission
- Single-asset backtests only so far — no portfolio-level position sizing yet
- Only one strategy exists (buy-and-hold) — nothing to actually compare it against yet
- The event loop is *designed* to avoid lookahead bias by only exposing the current day's price to the strategy, but I haven't written a test that actively tries to break this
- No risk-adjusted metrics yet (Sharpe, drawdown, etc.) — right now "did it work" just means "did the number go up," which isn't the full picture

## Roadmap

- **Week 1** ✅ complete — data layer, Order/Portfolio/Broker, event loop, buy-and-hold baseline, equity curve
- **Week 2**: SMA/EMA crossover, RSI mean-reversion, momentum strategies, commission/slippage modeling
- **Week 3**: Sharpe, Sortino, max drawdown, CAGR from scratch, walk-forward validation
- **Week 4**: comparison dashboard, packaging as a reusable module, write-up