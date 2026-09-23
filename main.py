from engine.data_loader import get_price_data
from engine.backtester import run_backtest
from strategies.buy_and_hold import generate_signal

from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

from strategies import sma_crossover
from strategies import rsi_strategy
from strategies import momentum_breakout



TICKER = "AAPL"

if __name__ == "__main__":
    price_data = get_price_data(TICKER, start = "2023-01-01", end = "2024-01-01")


    # BL
    bh_curve, bh_portfolio = run_backtest(
        price_data= price_data, ticker= TICKER, strategy_fn= generate_signal, starting_cash= 10000, commission= 1.0, slippage_pct=0.001,
    )

    print(f"BUY & HOLD final value: ${bh_curve[-1]['Total Value']:.2f} ({len(bh_portfolio.trade_log)} trades)")


    # SMA
    sma_curve, sma_portfolio = run_backtest(
        price_data= price_data, ticker= TICKER, strategy_fn= sma_crossover.generate_signal, prepare_fn= sma_crossover.prepare, starting_cash = 10000, commission= 1.0, slippage_pct=0.001,
    )

    print(f"SMA Crossover final value: ${sma_curve[-1]['Total Value']:.2f} ({len(sma_portfolio.trade_log)} trades)")


    # RSI 
    rsi_curve, rsi_portfolio = run_backtest(
        price_data= price_data, ticker= TICKER, strategy_fn= rsi_strategy.generate_signal, prepare_fn= rsi_strategy.prepare, starting_cash = 10000, commission= 1.0, slippage_pct=0.001,
    )

    print(f"RSI Mean-Reversion final value: ${rsi_curve[-1]['Total Value']:.2f} ({len(rsi_portfolio.trade_log)} trades)")


    mom_curve, mom_portfolio = run_backtest(
        price_data= price_data, ticker= TICKER, strategy_fn= momentum_breakout.generate_signal, prepare_fn= momentum_breakout.prepare, starting_cash = 10000, commission= 1.0, slippage_pct=0.001,
    )

    print(f"Momentum Breakout final value: ${mom_curve[-1]['Total Value']:.2f} ({len(mom_portfolio.trade_log)} trades)")


    