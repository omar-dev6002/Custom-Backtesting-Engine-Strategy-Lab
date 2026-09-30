"""
dashboard.py
Comparison visuals across all strategies - an overlaid equity curve chart
plus a Sharpe ratio bar chart, so the "no strategy wins everywhere" finding
is visible at a glance instead of buried in a table of numbers.
"""

import matplotlib.pyplot as plt
import pandas as pd

def plot_comparison(curves: dict, metrics: dict, output_path: str = "dashboard.png" ):
    """
        curves: {strategy_name: equity_curve} - equity_curve is the list of
            {"Date": ..., "Total Value": ...} dicts from run_backtest().
        metrics: {strategy_name: {"Sharpe": ..., ...}} - only "Sharpe" is used
            here, but the full metrics dict is accepted for convenience.
    """

    fig, (ax1, ax2) = plt.subplots(1,2, figsize = (16, 6))

    for name, curve in curves.items():
        df = pd.DataFrame(curve).set_index('Date')
        ax1.plot(df.index, df["Total Value"], label = name)

    ax1.set_title("Equity Curves - Strategy Comparison")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Portfolio Value ($)")
    ax1.legend()
    ax1.grid(True)

    names = list(metrics.keys())
    sharpes = [metrics[name]["Sharpe"] for name in names]
    bars = ax2.bar(names, sharpes)
    ax2.set_title("Sharpe Ratio Comparison")
    ax2.set_ylabel("Sharpe Ratio")
    ax2.axhline(0, color = "black", linewidth = 0.8)
    ax2.grid(True, axis = "y")
    plt.setp(ax2.get_xticklabels(), rotation = 20, ha = "right")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()