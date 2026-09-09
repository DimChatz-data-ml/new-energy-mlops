import os
import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

load_dotenv()

api_key = os.getenv("ENTSOE_API_KEY")

if not api_key:
    print('Key does not exist!')
    exit(1)

client = EntsoePandasClient(api_key=api_key)

end = pd.Timestamp.now(tz="Europe/Athens")
start = end - pd.Timedelta(days=2)

print("\n--- 1. PRICES ---")
try:
    df_prices = client.query_day_ahead_prices('GR', start=start, end=end)
    print("Type:", type(df_prices))
    print(df_prices.head(5))
except Exception as e:
    print(f"Error prices: {e}")

print("\n--- 2. LOAD ---")
try:
    df_load = client.query_load('GR', start=start, end=end)
    print("Type:", type(df_load))
    if isinstance(df_load, pd.DataFrame):
        print("Columns:", df_load.columns)
    print(df_load.head(5))
except Exception as e:
    print(f"Error load: {e}")

print("\n--- 3. GENERATION ---")
try:
    df_gen = client.query_generation('GR', start=start, end=end)
    print("Type:", type(df_gen))
    if isinstance(df_gen, pd.DataFrame):
        print("Columns:", df_gen.columns)
    print(df_gen.head(5).T)
except Exception as e:
    print(f"Error generation: {e}")

print("\n--- 4. WIND & SOLAR FORECAST ---")
try:
    df_ws = client.query_wind_and_solar_forecast('GR', start=start, end=end)
    print("Type:", type(df_ws))
    if isinstance(df_ws, pd.DataFrame):
        print("Columns:", df_ws.columns)
    print(df_ws.head(5))
except Exception as e:
    print(f"Error wind/solar: {e}")