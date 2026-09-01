from engine.data_loader import get_price_data 

if __name__ == "__main__":
    df = get_price_data("SPY", start = "2023-01-01", end = "2024-01-01")
    print(df.head())
    print(df.shape)

    