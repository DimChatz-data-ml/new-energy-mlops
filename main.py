import logging
from ingestion.create_table import create_all_tables
from ingestion.ingest_prices import extract_prices, load_prices
from ingestion.ingest_load import extract_load_mw, load_load_mw
from ingestion.ingest_generation import extract_generation, load_generation
from ingestion.ingest_wind_solar import extract_wind_solar, load_wind_solar
import pandas as pd
import time

logger = logging.getLogger(__name__)

countries = ['GR', 'DE_LU', 'FR']


def generate_date_chunks(start, end):
    points = list(pd.date_range(start=start, end=end, freq='28D'))
    if points[-1] != end:
        points.append(end)
    chunks = []
    for i in range(len(points) - 1):
        chunks.append((points[i], points[i + 1]))
    return chunks


def main():
    create_all_tables()
    start = pd.Timestamp("2020-01-01", tz="Europe/Athens")
    end = pd.Timestamp.now(tz="Europe/Athens")
    chunks = generate_date_chunks(start, end)

    for country in countries:
        for chunk in chunks:
            logger.info(f"prices | {country} | {chunk[0].date()} -> {chunk[1].date()}")
            try:
                df = extract_prices(country=country, start=chunk[0], end=chunk[1])
                time.sleep(3)
                load_prices(df)
            except Exception as e:
                logger.error(f'problem with prices, {country}, chunk {chunk}: {e}')

            logger.info(f"load | {country} | {chunk[0].date()} -> {chunk[1].date()}")
            try:
                df = extract_load_mw(country=country, start=chunk[0], end=chunk[1])
                time.sleep(3)
                load_load_mw(df)
            except Exception as e:
                logger.error(f'problem with load, {country}, chunk {chunk}: {e}')

            logger.info(f"generation | {country} | {chunk[0].date()} -> {chunk[1].date()}")
            try:
                df = extract_generation(country=country, start=chunk[0], end=chunk[1])
                time.sleep(3)
                load_generation(df)
            except Exception as e:
                logger.error(f'problem with generation, {country}, chunk {chunk}: {e}')

    # Wind/Solar forecast: μόνο μελλοντικό, εκτός date-chunk loop
    forecast_start = pd.Timestamp.now(tz="Europe/Athens")
    forecast_end = forecast_start + pd.Timedelta(days=2)
    for country in countries:
        logger.info(f"wind_solar | {country} | forecast {forecast_start.date()} -> {forecast_end.date()}")
        try:
            df = extract_wind_solar(country=country, start=forecast_start, end=forecast_end)
            time.sleep(3)
            load_wind_solar(df)
        except Exception as e:
            logger.error(f'problem with wind_solar, {country}: {e}')


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    main()