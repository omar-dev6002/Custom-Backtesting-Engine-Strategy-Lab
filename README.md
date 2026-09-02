# Custom Backtesting Engine & Strategy Lab

A backtesting engine built from scratch in Python — no `backtrader`, no `zipline`, no `bt`. The point isn't to reinvent those libraries, it's to actually understand what a backtester is doing under the hood: order execution, position tracking, and (eventually) the risk metrics everyone quotes without knowing how they're computed.

This is part of a 5-project, 5-month portfolio. Project 1 was a neural network from scratch; this one moves into quant finance.

## Status

Early. Data layer is done. Order/Broker/Portfolio classes (the actual engine) are next.

## What's built so far

- **`engine/data_loader.py`** — pulls daily OHLCV data via `yfinance`, caches it locally as CSV so I'm not hitting the API on every run. Handles the MultiIndex column format yfinance returns by default (flattens it to plain `Close/High/Low/Open/Volume` columns).

## Tickers

Starting with SPY, AAPL, MSFT, GOOGL, JPM — a mix of index ETF, tech megacaps, and financials, so I'm not just testing "does this work when tech goes up." All five are liquid enough that if a result looks weird, I can sanity-check it against any finance site.

## Setup

```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
python main.py
```

## Why build the engine instead of using a library

Most student "algo trading" projects call `backtrader` or `zipline`, plot one equity curve, and call it done. That tests whether you can read documentation, not whether you understand what's happening between a signal and a filled trade — slippage, commissions, position sizing, what happens when you try to sell something you don't hold. Building it myself means I have to make those decisions explicitly instead of inheriting someone else's defaults.

## Known limitations (will grow as the project does)

- No slippage or commission modeling yet — coming in Week 2
- Single-asset backtests only so far — no portfolio-level position sizing yet
- Not handling lookahead bias or survivorship bias yet — these are common ways student backtests lie to themselves, and I'll be explicit about how (or whether) I've avoided them once the engine is further along

## Roadmap

- **Week 1** (current): data layer + engine architecture (Order, Portfolio, Broker) + buy-and-hold baseline
- **Week 2**: SMA/EMA crossover, RSI mean-reversion, momentum breakout strategies + transaction costs
- **Week 3**: Sharpe, Sortino, max drawdown, CAGR from scratch + walk-forward validation
- **Week 4**: comparison dashboard, packaging as a reusable module, write-up
