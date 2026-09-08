from datetime import datetime
from engine.data_loader import get_price_data
from engine.backtester import run_backtest
from strategies.buy_and_hold import generate_signal


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

