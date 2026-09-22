import logging
import time
import json
from pathlib import Path
import pandas as pd

from ingestion.ingest_prices import extract_prices, load_prices
from ingestion.ingest_load import extract_load_mw, load_load_mw
from ingestion.ingest_generation import extract_generation, load_generation

logger = logging.getLogger("retry_missing")

# Τα 7 εναπομείναντα άδεια chunks από το Audit
TARGET_CHUNKS = [
    # 1. Prices DE_LU (1 chunk)
    {"data_type": "prices", "country": "DE_LU", "start": "2025-03-19 00:00:00+00", "end": "2025-04-16 00:00:00+00"},
    
    # 2. Prices FR (3 chunks)
    {"data_type": "prices", "country": "FR", "start": "2021-08-11 00:00:00+00", "end": "2021-09-08 00:00:00+00"},
    {"data_type": "prices", "country": "FR", "start": "2022-05-18 00:00:00+00", "end": "2022-06-15 00:00:00+00"},
    {"data_type": "prices", "country": "FR", "start": "2024-11-27 00:00:00+00", "end": "2024-12-25 00:00:00+00"},
    
    # 3. Load FR (2 chunks)
    {"data_type": "load", "country": "FR", "start": "2022-02-22 23:00:00+00", "end": "2022-03-23 00:00:00+00"},
    {"data_type": "load", "country": "FR", "start": "2024-06-11 23:00:00+00", "end": "2024-07-10 00:00:00+00"},
    
    # 4. Generation FR (1 chunk)
    {"data_type": "generation", "country": "FR", "start": "2020-07-15 00:00:00+00", "end": "2020-08-12 00:00:00+00"}
]


def run_retries():
    failures = []
    
    for i, target in enumerate(TARGET_CHUNKS, 1):
        dtype = target["data_type"]
        country = target["country"]
        start = pd.Timestamp(target["start"])
        end = pd.Timestamp(target["end"])
        
        logger.info(f"[{i}/{len(TARGET_CHUNKS)}] Retrying {dtype} | {country} | {start.date()} -> {end.date()}")
        
        try:
            if dtype == "prices":
                df = extract_prices(country=country, start=start, end=end)
                time.sleep(3)
                load_prices(df)
            elif dtype == "load":
                df = extract_load_mw(country=country, start=start, end=end)
                time.sleep(3)
                load_load_mw(df)
            elif dtype == "generation":
                df = extract_generation(country=country, start=start, end=end)
                time.sleep(3)
                load_generation(df)
            
            logger.info(f"SUCCESS: {dtype} | {country} | {start.date()} -> {end.date()}")

        except Exception as e:
            logger.error(f"FAILED: {dtype} | {country} | {start.date()} -> {end.date()} | Error: {e}")
            failures.append({
                "data_type": dtype,
                "country": country,
                "chunk_start": start,
                "chunk_end": end,
                "error": str(e)
            })

    # Αποθήκευση όσων αποτύχουν εκ νέου στο logs/failures.json
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    failures_file = logs_dir / "failures.json"
    
    with open(failures_file, "w", encoding="utf-8") as f:
        json.dump(failures, f, indent=2, ensure_ascii=False, default=str)
        
    logger.info(f"Done! {len(TARGET_CHUNKS) - len(failures)}/{len(TARGET_CHUNKS)} succeeded.")
    logger.info(f"Remaining failures saved to {failures_file} ({len(failures)} total).")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    run_retries()