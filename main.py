from engine.data_loader import get_multiple 
from engine.order import Order
from datetime import datetime
from engine.portfolio import Portfolio
from engine.broker import Broker



TICKERS = ['SPY', 'AAPL', 'MSFT', 'GOOGL', 'JPM']


test_order = Order(ticker = "AAPL", quantity = 10,side = "BUY", date = datetime(2023, 1, 3))
print(test_order)


try:
    bad_order = Order(ticker = "AAPL", quantity = -5,side = "BUY", date = datetime(2023, 1, 3))
    

except ValueError as e:
    print(f"Validation caught it: {e}")


if __name__ == "__main__":
    data = get_multiple(TICKERS, start = "2023-01-01", end = "2024-01-01")

    for ticker, df in data.items():
        print(f"{ticker}: {df.shape[0]} rows, from {df.index[0].date()} to {df.index[-1].date()} ")


portfolio = Portfolio(starting_cash= 100000)

# Day 1: buy 10 AAPL @ $125.07

portfolio.update_on_fill(ticker= "AAPL", quantity = 10, side = "BUY", fill_price = 125.07, commission = 1.0, date = datetime(2023, 1, 3))
print(f"After buy - cash: {portfolio.cash:.2f}, AAPL held: {portfolio.get_positions('AAPL')}")


# Day 200: sell all 10 AAPL @ $180

portfolio.update_on_fill(ticker = "AAPL", quantity = 10, side = "SELL", fill_price = 180.0, commission = 1.0, date = datetime(2023, 10, 15))
print(f"After sell - cash: {portfolio.cash:.2f}, AAPL held: {portfolio.get_positions('AAPL')}")


print(f"Trade log: {portfolio.trade_log}")



portfolio2 = Portfolio(starting_cash = 1000)
broker = Broker(portfolio = portfolio2, commission = 1.0)

order1 = Order(ticker = "AAPL", quantity = 5, side = "BUY", date = datetime(2023, 1, 3))
result1 = broker.execute(order1, fill_price = 125.07)
print(f"Order 1 filled: {result1}, cash now: {portfolio2.cash:.2f}")


order2 = Order(ticker = "AAPL", quantity = 10, side = "SELL", date = datetime(2023, 1, 4))
result2 = broker.execute(order2, fill_price = 130.00)
print(f"Order 2 filled: {result2}, cash now: {portfolio2.cash:.2f}")


order3 = Order(ticker = "MSFT", quantity = 100, side = "BUY", date = datetime(2023, 1, 5))
result3 = broker.execute(order3, fill_price = 300.00)
print(f"Order 3 filled: {result3}, cash now: {portfolio2.cash:.2f}")









