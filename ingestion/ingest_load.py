import logging
from psycopg2.extras import execute_values
from ingestion.api_connection import api_con_func
from ingestion.db_connection import create_connection
import pandas as pd

logger = logging.getLogger(__name__)


def extract_load_mw(country, start, end):
    client = api_con_func()
    df = client.query_load(country, start=start, end=end)
    df = df.reset_index()
    df['country'] = country
    df = df.rename(columns={'index': 'timestamp', 'Actual Load': 'actual_load'})

    return df


def load_load_mw(df):
    connection = create_connection()
    cursor = connection.cursor()

    data = list(
        df[['timestamp', 'actual_load', 'country']].itertuples(index=False, name=None)
    )

    query = """
        INSERT INTO load (timestamp, actual_load, country)
        VALUES %s
        ON CONFLICT (timestamp, country)
        DO UPDATE SET actual_load = EXCLUDED.actual_load
    """

    try:
        execute_values(cursor, query, data, page_size=5000)
        connection.commit()
        logger.info(
            f"load: bulk insert done, {len(data)} rows processed total"
        )

    except Exception:
        connection.rollback()
        logger.exception("load: bulk insert failed")
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

    df = extract_load_mw("GR", start, end)
    load_load_mw(df)
    load_load_mw(df)

    logger.info("It ran 2 times. Check pgadmin: SELECT COUNT(*) FROM load;")