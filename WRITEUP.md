I spent the last few months building a Python backtesting engine from scratch without Backtrader or Zipline. It runs four strategies with transaction costs and four risk metrics across five stocks over a four-year window. 

The headline result across 20 backtests was pretty humbled: plain buy-and-hold beat every active strategy I wrote on average return and Sharpe ratio.

Still, the most useful part of the project was spending three weeks completely wrong about my own results because of a single default argument.

My SMA Crossover strategy was supposed to buy when a fast moving average crosses above a slow one, and sell when it crosses below.

The function signature read:
def prepare(price_data, fast_window: int = 20, slow_window: int = 10):

Because 10 is smaller than 20, my "slow" window was actually twice as fast as my "fast" window. Instead of following trends, the strategy was buying dips and selling rallies. 

I didn't even spot it by reading the function. I only noticed because in an unrelated test, my SMA and RSI strategies placed trades on the exact same day for the exact same number of shares. Digging into that turned up a trade that executed before the 50-day moving average had enough days of data to exist. Every conclusion I had written down about the strategy's bear-market protection was describing an inverted model I didn't mean to build. I ended up leaving the broken numbers in the README right next to the corrected ones so the paper trail stayed intact.

Fixing that bug made me much more paranoid about the rest of the engine, so I changed a few things about how I was testing:

First, I stopped trusting single-year runs. My initial prototype tested one stock in 2023 and declared buy-and-hold the clear winner. Of course it won in 2023—that year was a steady uptrend. When I ran the exact same code on 2022, every strategy lost money, though the active ones that could exit positions lost less. Expanding to five tickers across four years showed how noisy short windows are: a different strategy had the top Sharpe ratio in three of the four years.

Second, I wrote 30 unit tests specifically to catch lookahead bias. Nobody accidentally includes tomorrow's price on purpose, but it is very easy to forget a .shift(1) or normalize against the mean of the full dataset instead of an expanding window. My test suite runs each strategy on the full price history, runs it again with everything after a cutoff date deleted, and checks that all signals up to the cutoff date match. To make sure the tests actually worked, I intentionally broke two strategies with a backward shift and full-series normalization just to watch the suite fail.

Third, I documented the execution flaw I chose not to fix yet. Right now, the engine generates a signal on today's close and fills the order at that same closing price. In live trading, once you know the closing price, the market is closed, so the earliest you can fill is tomorrow's open. Rather than rewrite the execution loop right away, I logged it in the docs as an optimistic bias that favors high-turnover strategies.

Once the SMA bug was fixed and the multi-year runs finished, buy-and-hold still led on average return, Sharpe, and Sortino, while a mean-reversion strategy kept the smallest average drawdown. Whether the year-to-year shifts in Sharpe ratio come from real market regimes or just small sample sizes (a handful of closed trades per year) is something I don't have enough data to prove yet.

The code, the test suite, and the commit fixing the SMA window bug are all up on GitHub: [link to repo]