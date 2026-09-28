import logging
import time
import json
from pathlib import Path
import pandas as pd
from ingestion.ingest_wind_solar import extract_wind_solar, load_wind_solar
from main import generate_date_chunks

logger = logging.getLogger(__name__)

countries = ['GR', 'DE_LU', 'FR']


def backfill_wind_solar():
    failures = []
    start = pd.Timestamp("2020-01-01", tz="UTC")
    end = pd.Timestamp.now(tz="UTC")
    chunks = generate_date_chunks(start, end)

    for country in countries:
        for chunk in chunks:
            logger.info(f"wind_solar | {country} | {chunk[0].date()} -> {chunk[1].date()}")
            try:
                df = extract_wind_solar(country=country, start=chunk[0], end=chunk[1])
                time.sleep(3)
                load_wind_solar(df)
            except Exception as e:
                logger.error(f'problem with wind_solar, {country}, chunk {chunk}: {e}')
                failures.append({
                    "data_type": "wind_solar",
                    "country": country,
                    "chunk_start": chunk[0],
                    "chunk_end": chunk[1],
                    "error": str(e)
                })

    if failures:
        logger.warning(f'we have {len(failures)} failures')
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        failures_file = logs_dir / "failures_wind_solar.json"
        with open(failures_file, "w", encoding="utf-8") as f:
            json.dump(failures, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Saved {len(failures)} failures to {failures_file}")
    else:
        logger.info("Wind/solar backfill complete with 0 failures!")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    backfill_wind_solar()