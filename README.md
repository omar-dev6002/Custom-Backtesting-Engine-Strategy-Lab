# Custom Backtesting Engine & Strategy Lab

A backtesting engine built from scratch in Python — no `backtrader`, no `zipline`, no `bt`. The point isn't to reinvent those libraries, it's to actually understand what a backtester is doing under the hood: order execution, position tracking, and (eventually) the risk metrics everyone quotes without knowing how they're computed.

This is part of a 5-project, 5-month portfolio. Project 1 was a neural network from scratch; this one moves into quant finance.

## Status

Week 2 complete. Full engine with 4 strategies, realistic transaction costs (commission + slippage), and position sizing. Week 3 (risk-adjusted metrics) is next.

## Results so far

All results: AAPL, 2023, $10,000 starting cash, $1 commission/trade, 0.1% slippage/trade, 25% position sizing (each trade risks at most 25% of available cash).

| Strategy | Final Value | Return | Trades |
|---|---|---|---|
| Buy & Hold | $11,343.23 | +13.4% | 1 |
| SMA Crossover (20/50) | $10,488.97 | +4.9% | 8 |
| RSI Mean-Reversion (14, 30/70) | $10,263.94 | +2.6% | 4 |
| Momentum Breakout (20-day) | $10,232.34 | +2.3% | 7 |

![Equity curve](equity_curve.png)

**The ranking (Buy & Hold > SMA > RSI ≈ Momentum) held even after adding position sizing**, which is a useful confirmation — it means the earlier finding (active strategies underperforming in this test) wasn't just an artifact of using 100% position sizes. It holds at a more conservative, realistic risk level too.

Why active strategies still lag here, in this specific test:

- 2023 AAPL was a strong, fairly persistent uptrend with relatively few deep pullbacks — close to the best-case scenario for buy-and-hold and the worst-case scenario for strategies that enter and exit.
- Every active strategy pays commission and slippage on every round-trip trade, both of which buy-and-hold largely avoids by only trading once.
- Each active strategy risks being *out* of the market during part of the rally — buy-and-hold can't miss any of it, by construction.

**What this result does NOT yet show:** whether these strategies took on less risk to get their (lower) returns. Week 3's risk-adjusted metrics (Sharpe ratio, max drawdown) will give a fairer comparison than raw final value alone. Testing across a choppier/sideways period and other tickers is also planned before drawing any general conclusions.

## What's built so far

- **`engine/data_loader.py`** — pulls daily OHLCV data via `yfinance`, caches it locally as CSV.
- **`engine/order.py`** — validated trade instruction (dataclass).
- **`engine/portfolio.py`** — cash, positions, trade log, and total value tracking.
- **`engine/broker.py`** — validates and executes orders. Models slippage (actual fill price is slightly worse than quoted, higher on buys, lower on sells) alongside a flat commission.
- **`engine/backtester.py`** — the event loop, with a `prepare_fn` hook for precomputing indicator columns and a `slippage_pct` parameter.
- **`engine/position_sizing.py`** — shared helper used by every strategy: caps each trade to a fixed percentage of available cash instead of betting the entire portfolio on one trade.
- **`strategies/buy_and_hold.py`** — baseline. Buys once (sized), holds.
- **`strategies/sma_crossover.py`** — trend-following, moving-average crossovers.
- **`strategies/rsi_strategy.py`** — mean-reversion, RSI thresholds.
- **`strategies/momentum_breakout.py`** — N-day high/low breakout, with the `.shift(1)` fix to avoid a self-referential comparison bug.

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

`derivations.md` has photographed handwritten notes (finance terms, hand-worked calculations, architecture design, the RSI formula, the breakout `.shift(1)` reasoning, slippage cost math, position sizing math) paired with typed explanations, day by day.

## Why build the engine instead of using a library

Most student "algo trading" projects call `backtrader` or `zipline`, plot one equity curve, and call it done. That tests whether you can read documentation, not whether you understand what's happening between a signal and a filled trade — slippage, commissions, position sizing, what happens when you try to sell something you don't hold. Building it myself means I have to make those decisions explicitly instead of inheriting someone else's defaults.

## Known limitations (will grow as the project does)

- Position sizing is a fixed percentage of cash, not a more sophisticated method (volatility-based sizing, Kelly criterion, etc.)
- Slippage model is a flat percentage, not dependent on order size, liquidity, or volatility
- Single-asset backtests only so far
- Only tested on one ticker, one year, one market regime (a strong uptrend) — the underperformance of all 3 active strategies is a hypothesis about that regime, not a general conclusion
- No risk-adjusted metrics yet (Sharpe, drawdown) — this is the biggest open gap in the current comparison, and Week 3's main focus
- RSI here uses simple rolling averages, not Wilder's exponential smoothing
- The event loop is *designed* to avoid lookahead bias by only exposing past-and-current data to the strategy, but I haven't written an active test that tries to break this

## Roadmap

- **Week 1** ✅ complete — data layer, Order/Portfolio/Broker, event loop, buy-and-hold baseline, equity curve
- **Week 2** ✅ complete — SMA crossover, RSI mean-reversion, momentum breakout, slippage modeling, position sizing. Consistent finding: buy-and-hold outperformed all active strategies in this test, even after position sizing was added
- **Week 3**: Sharpe, Sortino, max drawdown, CAGR from scratch, walk-forward validation
- **Week 4**: comparison dashboard, packaging as a reusable module, write-up