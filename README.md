# Custom Backtesting Engine & Strategy Lab

A backtesting engine built from scratch in Python — no `backtrader`, no `zipline`, no `bt`. The point isn't to reinvent those libraries, it's to actually understand what a backtester is doing under the hood: order execution, position tracking, and (eventually) the risk metrics everyone quotes without knowing how they're computed.

This is part of a 5-project, 5-month portfolio. Project 1 was a neural network from scratch; this one moves into quant finance.

## Status

Core engine pieces (Order, Portfolio, Broker) are built and individually tested. Next: wiring them into an event loop and running a first end-to-end backtest.

## What's built so far

- **`engine/data_loader.py`** — pulls daily OHLCV data via `yfinance`, caches it locally as CSV so I'm not hitting the API on every run. Handles the MultiIndex column format yfinance returns by default (flattens it to plain `Close/High/Low/Open/Volume` columns).
- **`engine/order.py`** — represents a single trade instruction (ticker, quantity, side, date). A `dataclass` with validation in `__post_init__` — rejects bad sides (must be `BUY`/`SELL`) and non-positive quantities immediately instead of letting the bug surface downstream.
- **`engine/portfolio.py`** — tracks cash, current holdings (a `{ticker: shares}` dict), and a full trade log. `update_on_fill()` is called by the Broker after every trade to update cash and positions. `total_value()` computes cash + market value of holdings — this is what the equity curve (Week 3) will plot over time. Tested against a hand-calculated buy/sell example (worked out on paper first, see `derivations.md`).
- **`engine/broker.py`** — the middleman between Order and Portfolio. Takes an order and a fill price, checks whether it's actually possible (enough cash to buy, enough shares held to sell), and only then updates the Portfolio. Rejects invalid orders instead of silently going negative. Tested all three paths: successful fill, sell-rejected (insufficient shares), buy-rejected (insufficient cash).

Bugs hit and fixed along the way: a type-hint typo (`starting_cash, float` instead of `starting_cash: float`) silently created two parameters instead of one; a stray `from matplotlib import ticker` autocomplete import masked a misspelled loop variable (`tiker`); and a file that saved as 0 bytes in VS Code, which threw a confusing `ImportError` before we traced it back to an unsaved file.

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

`derivations.md` has photographed handwritten notes (finance terms, hand-worked calculations) paired with typed explanations, day by day. Working things out on paper before coding them has been the main way I'm avoiding just pattern-matching syntax without understanding what it represents financially.

## Why build the engine instead of using a library

Most student "algo trading" projects call `backtrader` or `zipline`, plot one equity curve, and call it done. That tests whether you can read documentation, not whether you understand what's happening between a signal and a filled trade — slippage, commissions, position sizing, what happens when you try to sell something you don't hold. Building it myself means I have to make those decisions explicitly instead of inheriting someone else's defaults.

## Known limitations (will grow as the project does)

- No event loop yet — Order, Portfolio, and Broker all work individually but nothing yet runs a full day-by-day simulation
- No slippage modeling, only a flat per-trade commission
- Single-asset backtests only so far — no portfolio-level position sizing yet
- Not handling lookahead bias or survivorship bias yet — these are common ways student backtests lie to themselves, and I'll be explicit about how (or whether) I've avoided them once the engine is further along

## Roadmap

- **Week 1** (current): data layer + engine architecture (Order, Portfolio, Broker) + buy-and-hold baseline
  - Day 1 ✅ — env setup, repo structure, data loader with caching
  - Day 2 ✅ — Order class built and tested, Portfolio class built and tested
  - Day 3 ✅ — Broker class built and tested (fills + rejections)
  - Day 4 — wire Order → Broker → Portfolio into an event loop
  - Day 5 — buy-and-hold baseline strategy, first working end-to-end backtest + equity curve
  - Day 6 — buffer/debug day, Week 1 wrap-up
- **Week 2**: SMA/EMA crossover, RSI mean-reversion, momentum strategies, commission/slippage modeling
- **Week 3**: Sharpe, Sortino, max drawdown, CAGR from scratch, walk-forward validation
- **Week 4**: comparison dashboard, packaging as a reusable module, write-up