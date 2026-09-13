import logging
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
    counter = 0
    for index, row in df.iterrows():
        try:
            cursor.execute(
        """INSERT INTO load (timestamp, actual_load, country) 
        VALUES (%s, %s, %s) 
        ON CONFLICT (timestamp, country) 
        DO UPDATE SET actual_load = EXCLUDED.actual_load""",
        (row['timestamp'], row['actual_load'], row['country']))
            counter += 1
            if counter == 500:
                connection.commit()
                logger.info(f"load: committed 500 rows (up to index {index})")
                counter = 0

        except Exception as e:
            connection.rollback()
            logger.error(f'load: problem {e} in index {index}')

    connection.commit()
    logger.info(f"load: final commit done, {len(df)} rows processed total")
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
    load_load_mw(df)      # 1st time
    load_load_mw(df)      # 2nd time

    logger.info("It ran 2 times. Check pgadmin: SELECT COUNT(*) FROM load;")