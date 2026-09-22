import pandas as pd
from dotenv import load_dotenv
from ingestion.db_connection import create_connection

# Φόρτωση των μεταβλητών από το .env αρχείο
load_dotenv()

# Δημιουργία σύνδεσης με τη βάση
conn = create_connection()

tables = ["prices", "load", "generation"]

print("=== CHECKING FOR TIME GAPS > 1 HOUR ===")

for table in tables:
    if table == "generation":
        # Στο generation κάνουμε PARTITION ανά country & production_type
        partition_clause = "PARTITION BY country, production_type"
    else:
        partition_clause = "PARTITION BY country"

    query = f"""
    WITH time_diffs AS (
        SELECT 
            country,
            timestamp,
            LAG(timestamp) OVER ({partition_clause} ORDER BY timestamp) AS prev_ts
        FROM {table}
    )
    SELECT 
        country,
        prev_ts AS gap_start,
        timestamp AS gap_end,
        (timestamp - prev_ts) AS gap_duration
    FROM time_diffs
    WHERE timestamp - prev_ts > INTERVAL '1 hour'
    ORDER BY gap_duration DESC;
    """
    
    try:
        df = pd.read_sql(query, conn)
        print(f"\n--- Table: {table} ---")
        if df.empty:
            print("✅ CLEAN! Zero missing gaps > 1 hour found.")
        else:
            print(f"⚠️ Found {len(df)} gaps:")
            print(df.to_string(index=False))
    except Exception as e:
        print(f"\n--- Table: {table} ---")
        print(f"❌ Error querying table {table}: {e}")

conn.close()