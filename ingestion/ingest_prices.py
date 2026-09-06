from ingestion.api_connection import api_con_func
from ingestion.db_connection import create_connection
import pandas as pd   

def extract_prices(country,start,end):
    client=api_con_func()
    df=client.query_day_ahead_prices(country,start=start,end=end)
    df=df.to_frame(name="prices").reset_index()
    df['country']=country
    df=df.rename(columns={'index':'timestamp'})

    return df

def load_prices(df):
    connection=create_connection()
    cursor=connection.cursor()
    for index, row in df.iterrows():
        cursor.execute(
    """INSERT INTO prices (timestamp, prices, country) 
       VALUES (%s, %s, %s) 
       ON CONFLICT (timestamp, country) 
       DO UPDATE SET prices = EXCLUDED.prices""",
    (row['timestamp'], row['prices'], row['country'])
)  

    connection.commit()
    cursor.close()
    connection.close()



if __name__ == "__main__":
    end = pd.Timestamp.now(tz="Europe/Athens")
    start = end - pd.Timedelta(days=2)

    df = extract_prices("GR", start, end)
    load_prices(df)      # 1st time
    load_prices(df)      # 2nd time

    print("It ran 2 times.Check pgadmin: SELECT COUNT(*) FROM prices;")