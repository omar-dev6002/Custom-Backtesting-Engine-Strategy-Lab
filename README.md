# Custom Backtesting Engine & Strategy Lab

A backtesting engine built from scratch in Python — no `backtrader`, no `zipline`, no `bt`. The point isn't to reinvent those libraries, it's to actually understand what a backtester is doing under the hood: order execution, position tracking, and (eventually) the risk metrics everyone quotes without knowing how they're computed.

This is part of a 5-project, 5-month portfolio. Project 1 was a neural network from scratch; this one moves into quant finance.

## Status

Week 1 complete (engine core, buy-and-hold baseline). Week 2 in progress: two real strategies (SMA crossover, RSI mean-reversion) built, both compared against the baseline.

## Results so far

All results: AAPL, 2023, $10,000 starting cash.

| Strategy | Final Value | Return | Trades |
|---|---|---|---|
| Buy & Hold | $15,453.07 | +54.5% | 1 |
| SMA Crossover (20/50) | $12,219.04 | +22.2% | 8 |
| RSI Mean-Reversion (14, 30/70) | $11,180.46 | +11.8% | 4 |

![Equity curve](equity_curve.png)

**Both active strategies underperformed buy-and-hold, and both results are being kept, not hidden or parameter-tuned away.** A pattern emerging across both:

- 2023 was a fairly persistent uptrend year for AAPL. Buy-and-hold, by construction, can't be whipsawed or miss a rally waiting for a signal — it just holds through everything.
- SMA crossover pays commission on every round-trip (8 trades = ~4 round-trips) and reacts to trend changes late (moving averages lag by construction).
- RSI mean-reversion bets *against* the trend — it assumes an "overbought" reading means a pullback is coming, but in a genuine sustained uptrend, price can stay "overbought" for a long stretch while continuing to climb. Only 4 trades fired, suggesting the strategy mostly sat out or got timing wrong.

This is a fair testable hypothesis, not yet a conclusion: **one ticker, one year, one market regime isn't enough data to say these strategies "don't work"** — only that they didn't work under these specific conditions. Testing across a choppier/sideways period and other tickers is a planned next step, once there's a full lineup of strategies to compare properly.

## What's built so far

- **`engine/data_loader.py`** — pulls daily OHLCV data via `yfinance`, caches it locally as CSV.
- **`engine/order.py`** — validated trade instruction (dataclass).
- **`engine/portfolio.py`** — cash, positions, trade log, and total value tracking.
- **`engine/broker.py`** — validates and executes orders against the portfolio, rejecting infeasible trades.
- **`engine/backtester.py`** — the event loop. Takes an optional `prepare_fn` to add indicator columns to the price data before the loop starts — safe from lookahead bias since `pandas.rolling()` only ever looks backward from each row. Strategies receive the full day's `row` (price + any indicators), not just a bare price.
- **`strategies/buy_and_hold.py`** — baseline strategy. Buys max affordable shares once, holds.
- **`strategies/sma_crossover.py`** — trend-following. Buys when a fast moving average crosses above a slow one, sells on the reverse crossover.
- **`strategies/rsi_strategy.py`** — mean-reversion. Buys when RSI drops below 30 (oversold), sells when RSI rises above 70 (overbought). Uses a simple rolling-average RSI, not the exponentially-smoothed "Wilder's RSI" most trading platforms show — a known simplification worth revisiting later.

Bugs hit and fixed: multiple typos across sessions (`curent_prices`, `perpare`, a missing `df` prefix that silently created a 1-item list instead of a column reference), a stray autocomplete import that masked a misspelled loop variable, a 0-byte unsaved file, and a dict key naming mismatch. All caught by actually running the code and checking against expected/hand-calculated numbers.

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

`derivations.md` has photographed handwritten notes (finance terms, hand-worked calculations, architecture design, the RSI formula worked by hand) paired with typed explanations, day by day.

## Why build the engine instead of using a library

Most student "algo trading" projects call `backtrader` or `zipline`, plot one equity curve, and call it done. That tests whether you can read documentation, not whether you understand what's happening between a signal and a filled trade — slippage, commissions, position sizing, what happens when you try to sell something you don't hold. Building it myself means I have to make those decisions explicitly instead of inheriting someone else's defaults.

## Known limitations (will grow as the project does)

- No slippage modeling, only a flat per-trade commission
- Single-asset backtests only so far — no portfolio-level position sizing
- Only tested on one ticker, one year, one market regime (a strong uptrend) — the underperformance of both active strategies is a hypothesis about that regime, not a general conclusion
- No risk-adjusted metrics yet (Sharpe, drawdown) — comparisons so far are just "final dollar value," which doesn't account for how much risk was taken to get there
- RSI here uses simple rolling averages, not Wilder's exponential smoothing
- The event loop is *designed* to avoid lookahead bias by only exposing past-and-current data to the strategy, but I haven't written an active test that tries to break this

## Roadmap

- **Week 1** ✅ complete — data layer, Order/Portfolio/Broker, event loop, buy-and-hold baseline, equity curve
- **Week 2** (current):
  - Day 6 ✅ — refactored strategy interface to support indicators, built SMA crossover
  - Day 7 ✅ — built RSI mean-reversion, both active strategies underperforming baseline (documented, not hidden)
  - Remaining: momentum breakout, transaction cost/slippage modeling, position sizing, revisit why active strategies are losing to buy-and-hold
- **Week 3**: Sharpe, Sortino, max drawdown, CAGR from scratch, walk-forward validation
- **Week 4**: comparison dashboard, packaging as a reusable module, write-up