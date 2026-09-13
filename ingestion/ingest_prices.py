import logging
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
    counter = 0
    for index, row in df.iterrows():
        try:
            cursor.execute(
        """INSERT INTO prices (timestamp, price, country) 
        VALUES (%s, %s, %s) 
        ON CONFLICT (timestamp, country) 
        DO UPDATE SET price = EXCLUDED.price""",
        (row['timestamp'], row['price'], row['country']))
            counter += 1
            if counter == 500:
                connection.commit()
                logger.info(f"prices: committed 500 rows (up to index {index})")
                counter = 0

        except Exception as e:
            connection.rollback()
            logger.error(f'prices: problem {e} in index {index}')

    connection.commit()
    logger.info(f"prices: final commit done, {len(df)} rows processed total")
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
    load_prices(df)      # 1st time
    load_prices(df)      # 2nd time

    logger.info("It ran 2 times. Check pgadmin: SELECT COUNT(*) FROM prices;")