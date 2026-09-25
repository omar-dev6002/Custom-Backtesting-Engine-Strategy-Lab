# Custom Backtesting Engine & Strategy Lab

A backtesting engine built from scratch in Python — no `backtrader`, no `zipline`, no `bt`. The point isn't to reinvent those libraries, it's to actually understand what a backtester is doing under the hood: order execution, position tracking, and (eventually) the risk metrics everyone quotes without knowing how they're computed.

This is part of a 5-project, 5-month portfolio. Project 1 was a neural network from scratch; this one moves into quant finance.

## Status

Week 2 complete. Week 3 (risk-adjusted metrics) started: CAGR done, Sharpe/Sortino/max drawdown next.

## Results so far

All results: AAPL, 2023, $10,000 starting cash, $1 commission/trade, 0.1% slippage/trade, 25% position sizing.

| Strategy | Final Value | Return | CAGR | Trades |
|---|---|---|---|---|
| Buy & Hold | $11,343.23 | +13.4% | 13.68% | 1 |
| SMA Crossover (20/50) | $10,488.97 | +4.9% | 4.96% | 8 |
| RSI Mean-Reversion (14, 30/70) | $10,263.94 | +2.6% | 2.68% | 4 |
| Momentum Breakout (20-day) | $10,232.34 | +2.3% | 2.36% | 7 |

![Equity curve](equity_curve.png)

CAGR here is close to simple return since the backtest runs almost exactly 1 year — CAGR's real value is comparing strategies or backtests that ran for different lengths of time, which matters once testing expands beyond a single year.

**Buy & Hold still leads on every metric so far, and this continues to be documented honestly rather than adjusted to look different.** Why, in this specific test:

- 2023 AAPL was a strong, fairly persistent uptrend with relatively few deep pullbacks — close to the best-case scenario for buy-and-hold and the worst-case scenario for strategies that enter and exit.
- Every active strategy pays commission and slippage on every round-trip trade, both of which buy-and-hold largely avoids by only trading once.
- Each active strategy risks being *out* of the market during part of the rally — buy-and-hold can't miss any of it, by construction.

**What this doesn't yet show:** whether the active strategies took on less risk for their lower returns. That's exactly what Sharpe ratio and max drawdown (next) are for — return alone, even annualized as CAGR, still isn't the full picture.

## What's built so far

- **`engine/data_loader.py`** — pulls daily OHLCV data via `yfinance`, caches it locally as CSV.
- **`engine/order.py`** — validated trade instruction (dataclass).
- **`engine/portfolio.py`** — cash, positions, trade log, and total value tracking.
- **`engine/broker.py`** — validates and executes orders, models slippage alongside a flat commission.
- **`engine/backtester.py`** — the event loop, with a `prepare_fn` hook for indicators and a `slippage_pct` parameter.
- **`engine/position_sizing.py`** — caps each trade to a fixed percentage of available cash.
- **`engine/metrics.py`** — risk/return metrics computed from an equity curve. Currently has `to_returns_series()` (daily returns, the shared building block for every other metric) and `calculate_cagr()`.
- **`strategies/buy_and_hold.py`**, **`sma_crossover.py`**, **`rsi_strategy.py`**, **`momentum_breakout.py`** — 4 strategies, all using shared position sizing.

Bugs hit and fixed across sessions: multiple typos, a stray autocomplete import masking a misspelled loop variable, a 0-byte unsaved file, a dict key naming mismatch. All caught by running the code and checking against expected/hand-calculated numbers, not assumed to work.

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

`derivations.md` has photographed handwritten notes (finance terms, hand-worked calculations, architecture design, RSI formula, breakout `.shift(1)` reasoning, slippage math, position sizing math, CAGR derivation) paired with typed explanations, day by day.

## Why build the engine instead of using a library

Most student "algo trading" projects call `backtrader` or `zipline`, plot one equity curve, and call it done. That tests whether you can read documentation, not whether you understand what's happening between a signal and a filled trade — slippage, commissions, position sizing, what happens when you try to sell something you don't hold. Building it myself means I have to make those decisions explicitly instead of inheriting someone else's defaults.

## Known limitations (will grow as the project does)

- No risk-adjusted metrics yet beyond CAGR — Sharpe ratio and max drawdown are next, and are needed before any real conclusion about active vs. passive can be drawn
- Position sizing is a fixed percentage of cash, not volatility-based
- Slippage model is a flat percentage, not dependent on order size or liquidity
- Single-asset backtests only so far
- Only tested on one ticker, one year, one market regime (a strong uptrend)
- RSI uses simple rolling averages, not Wilder's exponential smoothing
- The event loop is *designed* to avoid lookahead bias but hasn't been actively tested against it

## Roadmap

- **Week 1** ✅ complete — data layer, Order/Portfolio/Broker, event loop, buy-and-hold baseline, equity curve
- **Week 2** ✅ complete — SMA crossover, RSI mean-reversion, momentum breakout, slippage modeling, position sizing
- **Week 3** (current):
  - Day 11 ✅ — daily returns, CAGR
  - Remaining: Sharpe ratio, Sortino ratio, max drawdown, walk-forward validation
- **Week 4**: comparison dashboard, packaging as a reusable module, write-up