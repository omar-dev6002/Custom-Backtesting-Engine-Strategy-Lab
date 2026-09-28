# Custom Backtesting Engine & Strategy Lab

A backtesting engine built from scratch in Python — no `backtrader`, no `zipline`, no `bt`. The point isn't to reinvent those libraries, it's to actually understand what a backtester is doing under the hood: order execution, position tracking, and the risk metrics everyone quotes without knowing how they're computed.

This is part of a 5-project, 5-month portfolio. Project 1 was a neural network from scratch; this one moves into quant finance.

## Status

Week 2 complete. Week 3 in progress: CAGR, Sharpe, and Sortino done. Max drawdown and walk-forward validation remaining.

## Results so far

All results: AAPL, 2023, $10,000 starting cash, $1 commission/trade, 0.1% slippage/trade, 25% position sizing.

| Strategy | Final Value | CAGR | Sharpe | Sortino | Trades |
|---|---|---|---|---|---|
| Buy & Hold | $11,343.23 | 13.68% | 2.13 | 3.31 | 1 |
| SMA Crossover (20/50) | $10,488.97 | 4.96% | 2.03 | 3.50 | 8 |
| RSI Mean-Reversion (14, 30/70) | $10,263.94 | 2.68% | 1.25 | 1.92 | 4 |
| Momentum Breakout (20-day) | $10,232.34 | 2.36% | 0.56 | 0.83 | 7 |

![Equity curve](equity_curve.png)

**The ranking depends on which metric you use.** On CAGR and Sharpe, Buy & Hold leads. On Sortino, SMA Crossover (3.50) edges ahead of Buy & Hold (3.31), the first time any active strategy has come out on top of the baseline on any metric.

Sortino differs from Sharpe by counting only downside volatility as risk. Sharpe penalizes upside swings just as much as downside ones, which is arguably unfair. A plausible explanation for the shift is that SMA sits in cash part of the time, so it avoids some of AAPL's down days entirely, leaving it with a smaller return but proportionally fewer bad days.

**This should not be read as "SMA beats Buy & Hold."** The Sortino gap is 0.19, measured on one ticker over one year with about 250 daily observations, small enough to plausibly be noise. The defensible claim is narrower: SMA is roughly comparable to Buy & Hold on a downside-adjusted basis, despite earning under half the return. Whether that holds up across other tickers and time periods is untested, and is what walk-forward validation is meant to probe.

RSI and Momentum trail on every metric, with Momentum consistently the weakest.

Why active strategies lagged on raw return in this test:

- 2023 AAPL was a strong, fairly persistent uptrend, close to the best case for buy-and-hold and the worst case for strategies that enter and exit.
- Every active strategy pays commission and slippage on each round-trip; buy-and-hold pays it once.
- Each active strategy is out of the market for part of the rally.

## What's built so far

- **`engine/data_loader.py`** — pulls daily OHLCV data via `yfinance`, caches it locally as CSV.
- **`engine/order.py`** — validated trade instruction (dataclass).
- **`engine/portfolio.py`** — cash, positions, trade log, and total value tracking.
- **`engine/broker.py`** — validates and executes orders, models slippage alongside a flat commission.
- **`engine/backtester.py`** — the event loop, with a `prepare_fn` hook for indicators and a `slippage_pct` parameter.
- **`engine/position_sizing.py`** — caps each trade to a fixed percentage of available cash.
- **`engine/metrics.py`** — `to_return_series()` (daily returns, shared building block), `calculate_cagr()`, `calculate_sharpe()`, `calculate_sortino()`. Sharpe and Sortino are annualized with a risk-free rate / target of 0.
- **`strategies/buy_and_hold.py`**, **`sma_crossover.py`**, **`rsi_strategy.py`**, **`momentum_breakout.py`** — 4 strategies, all using shared position sizing.

Bugs hit and fixed across sessions: multiple typos, a missing `()` on `.pct_change` that surfaced as an `AttributeError` two functions downstream, a stray autocomplete import, a 0-byte unsaved file, a dict key naming mismatch. All caught by running the code and checking against expected or hand-calculated numbers.

## Tickers

SPY, AAPL, MSFT, GOOGL, JPM — a mix of index ETF, tech megacaps, and financials, so results aren't just "does this work when tech goes up." So far only AAPL has actually been tested.

## Setup

```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
python main.py
```

## Notes and derivations

`derivations.md` has photographed handwritten notes (finance terms, hand-worked calculations, architecture design, RSI, breakout `.shift(1)` reasoning, slippage, position sizing, CAGR, Sharpe) paired with typed explanations, day by day. Sortino notes to be added.

## Why build the engine instead of using a library

Most student "algo trading" projects call `backtrader` or `zipline`, plot one equity curve, and call it done. That tests whether you can read documentation, not whether you understand what's happening between a signal and a filled trade — slippage, commissions, position sizing, what happens when you try to sell something you don't hold. Building it myself means I have to make those decisions explicitly instead of inheriting someone else's defaults.

## Known limitations (will grow as the project does)

- No max drawdown yet, which captures the single worst dip rather than average volatility
- Sharpe and Sortino use a risk-free rate / target of 0, not a real T-bill rate
- Sortino returns 0.0 for a strategy with no losing days, a crash-avoidance placeholder that would misread as "terrible" when it should be "no downside observed"
- Position sizing is a fixed percentage of cash, not volatility-based
- Slippage model is a flat percentage, not dependent on order size or liquidity
- Single-asset backtests only so far
- Only tested on one ticker, one year, one market regime (a strong uptrend), so the small metric differences between strategies are not statistically established
- RSI uses simple rolling averages, not Wilder's exponential smoothing
- The event loop is *designed* to avoid lookahead bias but hasn't been actively tested against it

## Roadmap

- **Week 1** ✅ complete — data layer, Order/Portfolio/Broker, event loop, buy-and-hold baseline, equity curve
- **Week 2** ✅ complete — SMA crossover, RSI mean-reversion, momentum breakout, slippage modeling, position sizing
- **Week 3** (current):
  - Day 11 ✅ — daily returns, CAGR
  - Day 12 ✅ — Sharpe ratio
  - Day 13 ✅ — Sortino ratio; ranking shifts, SMA edges Buy & Hold on downside-adjusted basis
  - Remaining: max drawdown, walk-forward validation
- **Week 4**: comparison dashboard, packaging as a reusable module, write-up