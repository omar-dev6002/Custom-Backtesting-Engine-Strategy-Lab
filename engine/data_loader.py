"""
data_loader.py
Fetches historical OHLCV price data for tickers, with local caching
so we don't hit the Yahoo Finance API every single run.
"""



import os
import pandas as pd
import yfinance as yf

DATA_DIR = "data"  # Directory to store cached data

def get_price_data(ticker: str, start : str, end: str) -> pd.DataFrame:
    """
        Return a DataFrame of daily OHLCV data for `ticker` between `start`
        and `end` (both 'YYYY-MM-DD' strings).
    
        Checks for a local CSV cache first. If not found, downloads from
        Yahoo Finance and saves a cache for next time.

    """
    os.makedirs(DATA_DIR, exist_ok = True)  # Ensure the data directory exists

    cache_path = os.path.join(DATA_DIR, f"{ticker}.csv")

    if os.path.exists(cache_path):
        df = pd.read_csv(cache_path, index_col = 0, parse_dates = True)
        print(f"[data_loader] Loaded {ticker} from cache ({len(df)} rows)")
        return df

    print(f"[data_loader] Downloading {ticker} from Yahoo Finance...")
    df = yf.download(ticker, start = start, end = end)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)     # Flatten MultiIndex columns if present (e.g., for ETFs)

    if df.empty:
        raise ValueError(f"No data returned for {ticker}. Check the symbol/date range.")

    df.to_csv(cache_path)
    print(f"[data_loader] Saved {ticker} to cache ({len(df)} rows)")
    return df


def get_multiple(tickers: list[str], start: str, end: str) -> dict[str, pd.DataFrame]:
    """Fetch price data for a list of tickers, returning {ticker: DataFrame}."""

    return {t: get_price_data(t, start, end) for t in tickers}

