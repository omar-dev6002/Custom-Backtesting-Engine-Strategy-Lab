from datetime import datetime
from engine.data_loader import get_price_data
from engine.backtester import run_backtest
from strategies.buy_and_hold import generate_signal
import matplotlib.pyplot as plt
import pandas as pd



TICKER = "AAPL"

if __name__ == "__main__":
    price_data = get_price_data(TICKER, start = "2023-01-01", end = "2024-01-01")

    equity_curve, portfolio = run_backtest(
        price_data = price_data,
        ticker = TICKER,
        strategy_fn = generate_signal,
        starting_cash = 10000,
        commission = 1.0,
    )

    print(f"Starting cash: $10,000.00")
    print(f"Final portfolio value: ${equity_curve[-1]['Total Value']:.2f}")
    print(f"Final cash: ${portfolio.cash:.2f}")
    print(f"Final AAPL held: {portfolio.get_positions(TICKER)}")
    print(f"Number of trades: {len(portfolio.trade_log)}")
    print(f"First trade: {portfolio.trade_log[0]}")

    equity_df = pd.DataFrame(equity_curve)
    equity_df.set_index("Date", inplace = True)

    plt.figure(figsize = (10,5))
    plt.plot(equity_df.index, equity_df['Total Value'])
    plt.title(f"Equity Curve - Buy & Hold {TICKER} (2023)")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("equity_curve.png")
    plt.show()




