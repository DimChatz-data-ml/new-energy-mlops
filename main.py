from ingestion.create_table import create_prices_table
from ingestion.ingest_prices import extract_prices,load_prices
import pandas as pd
import time

countries=['GR','DE_LU','FR']

def  generate_date_chunks(start, end):
    points=list(pd.date_range(start=start,end=end,freq='YS'))
    if points[-1]!=end:
        points.append(end)
    chunks=[]
    for i in range(len(points)-1):
        chunks.append((points[i],points[i+1]))
    return chunks    


def main():
    create_prices_table()
    start=pd.Timestamp("2020-01-01", tz="Europe/Athens")   
    end=pd.Timestamp.now(tz="Europe/Athens")
    chunks=generate_date_chunks(start, end)
    for country in countries:
        for chunk in chunks:
            df=extract_prices(country=country,start=chunk[0],end=chunk[1])
            time.sleep(3)
            load_prices(df)

if __name__ == "__main__":
    main()