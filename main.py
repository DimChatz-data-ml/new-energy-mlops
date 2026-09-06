from ingestion.create_table import create_prices_table
from ingestion.ingest_prices import extract_prices,load_prices
import pandas as pd

def main():
    create_prices_table()
    end=pd.Timestamp.now(tz="Europe/Athens")
    start=end- pd.Timedelta(days=2)
    df=extract_prices(country='GR',start=start,end=end)
    load_prices(df)

if __name__ == "__main__":
    main()