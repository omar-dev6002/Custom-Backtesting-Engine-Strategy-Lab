# Custom Backtesting Engine & Strategy Lab

A backtesting engine built from scratch in Python — no `backtrader`, no `zipline`, no `bt`. The point isn't to reinvent those libraries, it's to actually understand what a backtester is doing under the hood: order execution, position tracking, and the risk metrics everyone quotes without knowing how they're computed.

This is part of a 5-project, 5-month portfolio. Project 1 was a neural network from scratch; this one moves into quant finance.

## Main finding

Across 5 tickers (SPY, AAPL, MSFT, GOOGL, JPM) and 4 years (2020–2023), tested with realistic commission, slippage, and position sizing: **Buy & Hold led on average CAGR, Sharpe, and Sortino.** RSI Mean-Reversion had the smallest average drawdown.

| Strategy | Avg CAGR | Avg Sharpe | Avg Sortino | Avg Max Drawdown |
|---|---|---|---|---|
| Buy & Hold | 5.88% | **0.84** | **1.30** | −5.99% |
| RSI Mean-Reversion | 2.07% | 0.69 | 1.21 | **−3.98%** |
| SMA Crossover | 1.86% | 0.34 | 0.62 | −3.73% |
| Momentum Breakout | 1.75% | 0.39 | 0.66 | −4.53% |

That is an average over 20 separate backtests (5 tickers × 4 years), not one number. Looking at the individual years tells a different, more specific story: SMA Crossover had the best Sharpe of any strategy on AAPL in 2020 (1.84). Momentum Breakout had the best Sharpe on AAPL in 2021 (1.74). RSI had the best Sharpe on several tickers in 2022, the one bear-market year, where every strategy lost money and the question was only how much. Buy & Hold led on AAPL in 2023. No strategy won every year or every ticker — but averaged over all of them, simplicity won. The full 80-row table is in `walk_forward_all_tickers.csv`.

One row in that table is legitimately all zeros: RSI on JPM in 2021 made 0 trades, because RSI's 30/70 thresholds never triggered that year, so it held cash the entire time. A flat equity curve has zero variance, and `calculate_sharpe`/`calculate_sortino` return 0.0 by design in that case (see Day 12), rather than crashing on a division by zero. It is not a data error.

## A correction, kept rather than erased

Until partway through Week 4, the SMA Crossover strategy ran with the wrong parameters. Its `prepare()` function had `slow_window` defaulting to 10 instead of 50, so the "slow" average was shorter than the "fast" one, and the strategy was buying weakness and selling strength — close to the opposite of the trend-following rule it was supposed to test. Every SMA number published before the fix, and the conclusions built on them ("SMA is nearly as risk-efficient as Buy & Hold," "SMA gave real downside protection in 2022"), were wrong and have been retracted.

I found it because two strategies traded on the identical day in a 2020 test, and because SMA had traded before a 50-day average could exist. After the fix I added a check that rejects `fast_window >= slow_window`, and three tests in `tests/test_strategies.py` that pin the actual default values, so a silent change to a strategy parameter now fails the test suite instead of quietly changing every downstream number. Buy & Hold, RSI, and Momentum were unaffected, since they don't use that file.

## Known biases, and what was and wasn't tested for them

- **Lookahead bias.** `tests/test_lookahead.py` has 30 tests on synthetic data, checking two things: that an indicator computed on data cut off at day N exactly matches the same days computed on the full series, and that a strategy's equity curve up to day N is identical whether or not the data continues past it. Two deliberately broken strategies (one with a `shift(-1)` instead of `shift(1)`, one that normalizes against the mean of the *entire* series) are included specifically to confirm the tests fail when they should. All 30 pass against the real strategies.
- **Same-bar execution — not fixed, only documented.** A strategy decides using today's close and is filled at that same close. Real trading can't do that; the earliest a real order could fill is the next day's open. This test suite can't catch it, because it isn't a future-row leak, it's an assumption built into every fill in the engine. Every number in this README is probably slightly optimistic because of it, more so for the strategies that trade often.
- **Survivorship bias — not mitigated.** All 5 tickers tested are companies that performed well enough to still be widely held today. A basket that included stocks that were delisted or collapsed over 2020–2023 would likely show a smaller gap, or none, between Buy & Hold and the active strategies.
- **No statistical significance testing.** Each strategy closes somewhere between 0 and 11 round trips per ticker-year. The year-by-year Sharpe "winners" above are consistent with real regime effects, but are also consistent with a small sample producing a different winner by chance each time. The 20-backtest average is more robust than any single year, but still not large enough to claim statistical significance.

## Results (single ticker, AAPL, 2023, for a worked example)

$10,000 starting cash, $1 commission per trade, 0.1% slippage, 25% position sizing.

| Strategy | Final Value | CAGR | Sharpe | Sortino | Max Drawdown | Trades | Win Rate |
|---|---|---|---|---|---|---|---|
| Buy & Hold | $11,343.23 | 13.68% | 2.13 | 3.31 | −5.07% | 1 | n/a |
| SMA Crossover (20/50) | $10,061.97 | 0.63% | 0.59 | 0.99 | −0.71% | 1 | n/a |
| RSI Mean-Reversion (14, 30/70) | $10,263.94 | 2.68% | 1.25 | 1.92 | −1.87% | 4 | 100% (2 of 2) |
| Momentum Breakout (20-day) | $10,232.34 | 2.36% | 0.56 | 0.83 | −5.99% | 7 | 33% (1 of 3) |

Win rate counts only closed round trips (a buy followed by its sell). Buy & Hold never sells, and SMA bought once in 2023 and never sold, so neither has a win rate.

![Strategy comparison dashboard](dashboard.png)

## What's built

- **`engine/data_loader.py`** — daily OHLCV from `yfinance`, cached as CSV, filename keyed to ticker and date range.
- **`engine/order.py`**, **`portfolio.py`**, **`broker.py`** — validated orders, cash and position tracking, execution with a flat commission and percentage slippage.
- **`engine/backtester.py`** — the event loop, with a `prepare_fn` hook for indicators.
- **`engine/position_sizing.py`** — caps each trade to a fixed share of available cash (25% here).
- **`engine/metrics.py`** — daily returns, CAGR, Sharpe, Sortino, max drawdown, win rate.
- **`engine/walk_forward.py`** — splits multi-year data into yearly windows and runs every strategy on every window, every ticker.
- **`engine/dashboard.py`** — overlaid equity curve chart plus a Sharpe bar chart.
- **`strategies/`** — buy-and-hold, SMA crossover (20/50), RSI mean-reversion (14, 30/70), momentum breakout (20-day).
- **`tests/test_metrics.py`** (9 tests) — the metric functions against hand-worked examples in `derivations.md`, plus win-rate edge cases.
- **`tests/test_strategies.py`** (5 tests) — pins the SMA, RSI, and Momentum default parameters, and the `fast_window < slow_window` guard, added after the SMA bug.
- **`tests/test_lookahead.py`** (30 tests) — the lookahead checks described above.
- **`pyproject.toml`** — installable with `pip install -e .`, verified importable from outside the project folder.

44 tests, all passing, run with `python -m pytest`.

Bugs hit and fixed across the project: multiple typos, a missing `()` on `.pct_change`, a stray autocomplete import, a 0-byte unsaved file more than once, a dict key naming mismatch, a cache-collision bug that silently returned one year of data when four were requested, two separate environment issues (`pytest` installed outside the venv, a missing `tests/__init__.py`), and the SMA default-parameter bug above, which is the one that actually changed a published conclusion.

## Setup

```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
python main.py
```

Editable install, for use in another project:
```bash
pip install -e .
```

Tests:
```bash
python -m pip install pytest
python -m pytest
```

## Notes and derivations

`derivations.md` has photographed handwritten notes paired with typed explanations: finance terms, the architecture, indicator math, slippage, position sizing, CAGR, and Sharpe, day by day.

## Why build the engine instead of using a library

Most student "algo trading" projects call `backtrader` or `zipline`, plot one equity curve, and call it done. That tests whether you can read documentation, not whether you understand what's happening between a signal and a filled trade. Building it myself meant making those decisions explicitly — and, as the SMA correction above shows, being accountable when one of them was wrong, rather than quietly fixing it and deleting the evidence.

## Remaining limitations

- Same-bar execution (see bias section) is documented, not fixed.
- Survivorship bias (see bias section) is documented, not mitigated.
- Position sizing is a fixed 25% of cash, not volatility-based.
- Slippage is a flat 0.1%, not dependent on order size or liquidity.
- Single-asset backtests only — no portfolio-level diversification across tickers at once.
- Walk-forward windows run independently, not chained, which understates strategies with long indicator warm-ups (SMA's 50-day window especially).
- Sharpe and Sortino use a risk-free rate and target of 0.
- RSI uses a simple rolling average, not Wilder's exponential smoothing.
- `requirements.txt` and `pyproject.toml` list the same dependencies by hand, in two places.

## Roadmap

- **Weeks 1–3**: data layer, engine, four strategies, slippage, position sizing, risk metrics, walk-forward validation. Complete.
- **Week 4**: dashboard, packaging, unit tests (metrics, strategy parameters, lookahead bias), the SMA correction, the multi-ticker run, this bias section. Complete.
- **Remaining**: public write-up.