import os
import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient

load_dotenv()

api_key=os.getenv("ENTSOE_API_KEY")

if not api_key:
    print('key does not exist!')
    exit(1)

client=EntsoePandasClient(api_key=api_key)

end=pd.Timestamp.now(tz="Europe/Athens")
start=end- pd.Timedelta(days=2)

try:
    df=client.query_day_ahead_prices('GR', start=start, end=end)
    print('everything is OK,we have data')
    df = df.to_frame(name='prices').reset_index()
    df['country'] = 'GR'
    df=df.rename(columns={'index':'timestamp'})
    print(df)
except Exception as e:
    print(f"error fetching data {e}")
    exit(1)









