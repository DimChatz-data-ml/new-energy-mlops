import pandas as pd
from ingestion.ingest_generation import extract_generation

start = pd.Timestamp("2026-05-15", tz="UTC")
end = pd.Timestamp("2026-05-16", tz="UTC")

df = extract_generation(country="FR", start=start, end=end)
coal_rows = df[df['production_type'].str.contains('Hard coal', case=False, na=False)]
print(coal_rows)