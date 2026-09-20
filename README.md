# Custom Backtesting Engine & Strategy Lab

A backtesting engine built from scratch in Python — no `backtrader`, no `zipline`, no `bt`. The point isn't to reinvent those libraries, it's to actually understand what a backtester is doing under the hood: order execution, position tracking, and (eventually) the risk metrics everyone quotes without knowing how they're computed.

This is part of a 5-project, 5-month portfolio. Project 1 was a neural network from scratch; this one moves into quant finance.

## Status

Week 1 complete (engine core, buy-and-hold baseline). Week 2 in progress: first real strategy (SMA crossover) built and compared against the baseline.

## Results so far

All results: AAPL, 2023, $10,000 starting cash.

| Strategy | Final Value | Return | Trades |
|---|---|---|---|
| Buy & Hold | $15,453.07 | +54.5% | 1 |
| SMA Crossover (20/50) | $12,219.04 | +22.2% | 8 |

![Equity curve](equity_curve.png)

**SMA crossover underperformed buy-and-hold, and that result is being kept, not hidden.** A few likely reasons, worth investigating further rather than dismissing:

- 8 trades means ~4 round-trips, each paying commission twice — that's real drag on returns that buy-and-hold never incurs.
- Moving averages are lagging indicators by construction — they confirm a trend only after it's partly over, so entries and exits both happen a bit late.
- 2023 was a fairly persistent uptrend year for AAPL. That's close to the worst-case scenario for a trend-following strategy that keeps entering and exiting — "just hold and don't touch it" tends to win when the underlying trend doesn't reverse much.

Next step on this: test different SMA windows and a choppier/sideways period to see if the strategy performs better where it's theoretically supposed to.

## What's built so far

- **`engine/data_loader.py`** — pulls daily OHLCV data via `yfinance`, caches it locally as CSV.
- **`engine/order.py`** — validated trade instruction (dataclass).
- **`engine/portfolio.py`** — cash, positions, trade log, and total value tracking.
- **`engine/broker.py`** — validates and executes orders against the portfolio, rejecting infeasible trades.
- **`engine/backtester.py`** — the event loop. Takes an optional `prepare_fn` to add indicator columns (e.g. moving averages) to the price data before the loop starts — safe from lookahead bias since `pandas.rolling()` only ever looks backward from each row. Strategies receive the full day's `row` (price + any indicators), not just a bare price.
- **`strategies/buy_and_hold.py`** — baseline strategy. Buys max affordable shares once, holds. Checks the portfolio directly for current position rather than tracking a separate flag.
- **`strategies/sma_crossover.py`** — buys when a fast moving average crosses above a slow one (uptrend signal), sells when it crosses back below. Crossover points are precomputed vectorized with pandas rather than detected inside the loop.

Bugs hit and fixed: multiple typos across sessions (`curent_prices`, `perpare`, a missing `df` prefix that silently created a 1-item list instead of a column reference and threw a length-mismatch error), a stray autocomplete import that masked a misspelled loop variable, a 0-byte unsaved file, and a dict key naming mismatch. All caught by actually running the code and checking against expected numbers, not by assuming it worked.

## Tickers

SPY, AAPL, MSFT, GOOGL, JPM — a mix of index ETF, tech megacaps, and financials, so results aren't just "does this work when tech goes up."

## Setup

```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
python main.py
```

## Notes and derivations

`derivations.md` has photographed handwritten notes (finance terms, hand-worked calculations, architecture design) paired with typed explanations, day by day.

## Why build the engine instead of using a library

Most student "algo trading" projects call `backtrader` or `zipline`, plot one equity curve, and call it done. That tests whether you can read documentation, not whether you understand what's happening between a signal and a filled trade — slippage, commissions, position sizing, what happens when you try to sell something you don't hold. Building it myself means I have to make those decisions explicitly instead of inheriting someone else's defaults.

## Known limitations (will grow as the project does)

- No slippage modeling, only a flat per-trade commission
- Single-asset backtests only so far — no portfolio-level position sizing
- Only tested on one ticker, one year, one market regime (a strong uptrend) — not enough to draw real conclusions about either strategy yet
- No risk-adjusted metrics yet (Sharpe, drawdown) — comparisons so far are just "final dollar value," which is a weak way to judge a strategy on its own
- The event loop is *designed* to avoid lookahead bias by only exposing past-and-current data to the strategy, but I haven't written an active test that tries to break this

## Roadmap

- **Week 1** ✅ complete — data layer, Order/Portfolio/Broker, event loop, buy-and-hold baseline, equity curve
- **Week 2** (current):
  - Day 6 ✅ — refactored strategy interface to support indicators, built and tested SMA crossover, documented underperformance vs. buy-and-hold
  - Remaining: RSI mean-reversion, momentum breakout, transaction cost/slippage modeling, position sizing
- **Week 3**: Sharpe, Sortino, max drawdown, CAGR from scratch, walk-forward validation
- **Week 4**: comparison dashboard, packaging as a reusable module, write-up