# Custom Backtesting Engine & Strategy Lab

A backtesting engine built from scratch in Python — no `backtrader`, no `zipline`, no `bt`. The point isn't to reinvent those libraries, it's to actually understand what a backtester is doing under the hood: order execution, position tracking, and (eventually) the risk metrics everyone quotes without knowing how they're computed.

This is part of a 5-project, 5-month portfolio. Project 1 was a neural network from scratch; this one moves into quant finance.

## Status

Week 1 complete. Week 2: 3 active strategies now built (SMA crossover, RSI mean-reversion, momentum breakout) alongside the buy-and-hold baseline. Transaction cost modeling and position sizing remaining for Week 2.

## Results so far

All results: AAPL, 2023, $10,000 starting cash.

| Strategy | Final Value | Return | Trades |
|---|---|---|---|
| Buy & Hold | $15,453.07 | +54.5% | 1 |
| SMA Crossover (20/50) | $12,219.04 | +22.2% | 8 |
| RSI Mean-Reversion (14, 30/70) | $11,180.46 | +11.8% | 4 |
| Momentum Breakout (20-day) | $10,925.85 | +9.3% | 7 |

![Equity curve](equity_curve.png)

**Every active strategy underperformed buy-and-hold, and this is documented honestly, not tuned away.** This is a specific, understandable result, not a general verdict on active trading:

- 2023 AAPL was a strong, fairly persistent uptrend with relatively few deep pullbacks — close to the best-case scenario for buy-and-hold and the worst-case scenario for strategies that enter and exit.
- Every active strategy pays commission on every round-trip trade, which buy-and-hold structurally avoids by only trading once.
- Each strategy risks being *out* of the market during part of the rally — buy-and-hold can't miss any of it, by construction.

**What this result does NOT yet show:** whether these strategies took on less risk to get their (lower) returns. "Final dollar value" alone is a weak metric — Week 3 adds Sharpe ratio and max drawdown, which will give a fairer, risk-adjusted comparison. It's entirely possible an active strategy that "lost" on raw return looks more attractive once volatility and drawdown are accounted for. Testing across a choppier/sideways period and other tickers is also planned, since one ticker/one year/one uptrend regime isn't enough to generalize from.

## What's built so far

- **`engine/data_loader.py`** — pulls daily OHLCV data via `yfinance`, caches it locally as CSV.
- **`engine/order.py`** — validated trade instruction (dataclass).
- **`engine/portfolio.py`** — cash, positions, trade log, and total value tracking.
- **`engine/broker.py`** — validates and executes orders against the portfolio, rejecting infeasible trades.
- **`engine/backtester.py`** — the event loop, with a `prepare_fn` hook for precomputing indicator columns (lookahead-safe via `pandas.rolling()`).
- **`strategies/buy_and_hold.py`** — baseline. Buys once, holds.
- **`strategies/sma_crossover.py`** — trend-following. Buy/sell on moving-average crossovers.
- **`strategies/rsi_strategy.py`** — mean-reversion. Buy oversold (RSI<30), sell overbought (RSI>70).
- **`strategies/momentum_breakout.py`** — buys when price breaks above its N-day high, sells below its N-day low. Uses `.shift(1)` before the rolling max/min so today's price is compared against the *prior* N days only — without this, a breakout above a window that includes today's own price is mathematically impossible to detect.

Bugs hit and fixed across sessions: multiple typos (`curent_prices`, `perpare`, a missing `df` prefix), a stray autocomplete import masking a misspelled loop variable, a 0-byte unsaved file, a dict key naming mismatch. All caught by running the code and checking against expected/hand-calculated numbers, not assumed to work.

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

`derivations.md` has photographed handwritten notes (finance terms, hand-worked calculations, architecture design, the RSI formula worked by hand, the breakout `.shift(1)` reasoning) paired with typed explanations, day by day.

## Why build the engine instead of using a library

Most student "algo trading" projects call `backtrader` or `zipline`, plot one equity curve, and call it done. That tests whether you can read documentation, not whether you understand what's happening between a signal and a filled trade — slippage, commissions, position sizing, what happens when you try to sell something you don't hold. Building it myself means I have to make those decisions explicitly instead of inheriting someone else's defaults.

## Known limitations (will grow as the project does)

- No slippage modeling, only a flat per-trade commission
- Single-asset backtests only so far — no portfolio-level position sizing
- Only tested on one ticker, one year, one market regime (a strong uptrend) — the underperformance of all 3 active strategies is a hypothesis about that regime, not a general conclusion
- No risk-adjusted metrics yet (Sharpe, drawdown) — this is the biggest open gap in the current comparison, since "final value" ignores how much risk each strategy took on
- RSI here uses simple rolling averages, not Wilder's exponential smoothing
- The event loop is *designed* to avoid lookahead bias by only exposing past-and-current data to the strategy, but I haven't written an active test that tries to break this

## Roadmap

- **Week 1** ✅ complete — data layer, Order/Portfolio/Broker, event loop, buy-and-hold baseline, equity curve
- **Week 2** (current):
  - Day 6 ✅ — refactored strategy interface, built SMA crossover
  - Day 7 ✅ — built RSI mean-reversion
  - Day 8 ✅ — built momentum breakout, all 4 strategies now comparable, all active strategies underperform baseline
  - Remaining: transaction cost/slippage modeling, position sizing
- **Week 3**: Sharpe, Sortino, max drawdown, CAGR from scratch, walk-forward validation
- **Week 4**: comparison dashboard, packaging as a reusable module, write-up