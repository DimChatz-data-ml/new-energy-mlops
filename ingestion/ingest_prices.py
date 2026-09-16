import logging
from psycopg2.extras import execute_values
from ingestion.api_connection import api_con_func
from ingestion.db_connection import create_connection
import pandas as pd

logger = logging.getLogger(__name__)


def extract_prices(country, start, end):
    client = api_con_func()
    df = client.query_day_ahead_prices(country, start=start, end=end)
    df = df.to_frame(name="price").reset_index()
    df['country'] = country
    df = df.rename(columns={'index': 'timestamp'})

    return df


def load_prices(df):
    connection = create_connection()
    cursor = connection.cursor()

    data = list(
        df[['timestamp', 'price', 'country']].itertuples(index=False, name=None)
    )

    query = """
        INSERT INTO prices (timestamp, price, country)
        VALUES %s
        ON CONFLICT (timestamp, country)
        DO UPDATE SET price = EXCLUDED.price
    """

    try:
        execute_values(cursor, query, data, page_size=5000)
        connection.commit()
        logger.info(
            f"prices: bulk insert done, {len(data)} rows processed total"
        )

    except Exception:
        connection.rollback()
        logger.exception("prices: bulk insert failed")
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    end = pd.Timestamp.now(tz="Europe/Athens")
    start = end - pd.Timedelta(days=2)

    df = extract_prices("GR", start, end)
    load_prices(df)
    load_prices(df)

    logger.info("It ran 2 times. Check pgadmin: SELECT COUNT(*) FROM prices;")