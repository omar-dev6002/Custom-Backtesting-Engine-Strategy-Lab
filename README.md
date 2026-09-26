# Custom Backtesting Engine & Strategy Lab

A backtesting engine built from scratch in Python — no `backtrader`, no `zipline`, no `bt`. The point isn't to reinvent those libraries, it's to actually understand what a backtester is doing under the hood: order execution, position tracking, and (eventually) the risk metrics everyone quotes without knowing how they're computed.

This is part of a 5-project, 5-month portfolio. Project 1 was a neural network from scratch; this one moves into quant finance.

## Status

Week 2 complete. Week 3 in progress: CAGR and Sharpe ratio done, revealing a real nuance the earlier return-only comparison missed. Sortino, max drawdown, walk-forward validation remaining.

## Results so far

All results: AAPL, 2023, $10,000 starting cash, $1 commission/trade, 0.1% slippage/trade, 25% position sizing.

| Strategy | Final Value | CAGR | Sharpe | Trades |
|---|---|---|---|---|
| Buy & Hold | $11,343.23 | 13.68% | 2.13 | 1 |
| SMA Crossover (20/50) | $10,488.97 | 4.96% | 2.03 | 8 |
| RSI Mean-Reversion (14, 30/70) | $10,263.94 | 2.68% | 1.25 | 4 |
| Momentum Breakout (20-day) | $10,232.34 | 2.36% | 0.56 | 7 |

![Equity curve](equity_curve.png)

**Sharpe ratio reveals something the raw return comparison completely missed: SMA Crossover is nearly as risk-efficient as Buy & Hold, despite earning less than half the CAGR (4.96% vs 13.68%).** Sharpe of 2.03 vs. 2.13 is a small gap — meaning SMA achieved a smoother, lower-volatility path to its lower total return, roughly proportional to the risk it took on. This is a genuinely different conclusion than "SMA underperformed," which is what the Week 2 return-only comparison suggested.

RSI (Sharpe 1.25) and Momentum (Sharpe 0.56) both still trail clearly, even risk-adjusted — Momentum in particular shows the weakest risk-adjusted efficiency of any strategy tested so far.

**Why this matters, and why it was worth waiting for:** "final dollar value" and even CAGR both ignore *how bumpy the ride was* to get there. Sharpe divides return by volatility, so two strategies with very different total returns can turn out to be similarly efficient once risk is accounted for. This is exactly the kind of result that gets lost if you only look at one metric — which is the whole reason this project builds multiple metrics rather than declaring a single "winner" number.

Max drawdown (next) will add another angle: not just how volatile the ride was on average, but how bad the single worst dip actually got.

## What's built so far

- **`engine/data_loader.py`** — pulls daily OHLCV data via `yfinance`, caches it locally as CSV.
- **`engine/order.py`** — validated trade instruction (dataclass).
- **`engine/portfolio.py`** — cash, positions, trade log, and total value tracking.
- **`engine/broker.py`** — validates and executes orders, models slippage alongside a flat commission.
- **`engine/backtester.py`** — the event loop, with a `prepare_fn` hook for indicators and a `slippage_pct` parameter.
- **`engine/position_sizing.py`** — caps each trade to a fixed percentage of available cash.
- **`engine/metrics.py`** — `to_return_series()` (daily returns, shared building block), `calculate_cagr()`, `calculate_sharpe()` (annualized, risk-free rate simplified to 0).
- **`strategies/buy_and_hold.py`**, **`sma_crossover.py`**, **`rsi_strategy.py`**, **`momentum_breakout.py`** — 4 strategies, all using shared position sizing.

Bugs hit and fixed across sessions: multiple typos, a missing `()` on `.pct_change` (calling the method reference itself instead of its result, causing an `AttributeError` two functions downstream), a stray autocomplete import, a 0-byte unsaved file, a dict key naming mismatch. All caught by running the code and checking against expected/hand-calculated numbers, not assumed to work.

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

`derivations.md` has photographed handwritten notes (finance terms, hand-worked calculations, architecture design, RSI formula, breakout `.shift(1)` reasoning, slippage math, position sizing math, CAGR derivation, Sharpe ratio calculation) paired with typed explanations, day by day.

## Why build the engine instead of using a library

Most student "algo trading" projects call `backtrader` or `zipline`, plot one equity curve, and call it done. That tests whether you can read documentation, not whether you understand what's happening between a signal and a filled trade — slippage, commissions, position sizing, what happens when you try to sell something you don't hold. Building it myself means I have to make those decisions explicitly instead of inheriting someone else's defaults.

## Known limitations (will grow as the project does)

- No Sortino ratio or max drawdown yet — both add angles Sharpe alone doesn't capture (Sortino only penalizes downside volatility; drawdown captures the single worst dip, not just average bumpiness)
- Sharpe's risk-free rate is simplified to 0, not a real T-bill rate
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
  - Day 12 ✅ — Sharpe ratio, revealed SMA's risk-adjusted efficiency nearly matches Buy & Hold
  - Remaining: Sortino ratio, max drawdown, walk-forward validation
- **Week 4**: comparison dashboard, packaging as a reusable module, write-up