import logging
from psycopg2.extras import execute_values
from ingestion.api_connection import api_con_func
from ingestion.db_connection import create_connection
import pandas as pd

logger = logging.getLogger(__name__)


def extract_generation(country, start, end):
    client = api_con_func()
    df = client.query_generation(country, start=start, end=end)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
        " - ".join([str(e) for e in col if e]).strip()
        for col in df.columns
    ]

    df = df.reset_index()
    df = df.rename(columns={'index': 'timestamp'})
    df = df.melt(
        id_vars=['timestamp'],
        var_name='production_type',
        value_name='quantity_mw'
    )
    df['country'] = country

    return df


def load_generation(df):
    connection = create_connection()
    cursor = connection.cursor()

    data = list(
        df[
            ['timestamp', 'production_type', 'quantity_mw', 'country']
        ].itertuples(index=False, name=None)
    )

    query = """
        INSERT INTO generation
            (timestamp, production_type, quantity_mw, country)
        VALUES %s
        ON CONFLICT (timestamp, country, production_type)
        DO UPDATE SET quantity_mw = EXCLUDED.quantity_mw
    """

    try:
        execute_values(cursor, query, data, page_size=5000)
        connection.commit()
        logger.info(
            f"generation: bulk insert done, {len(data)} rows processed total"
        )

    except Exception:
        connection.rollback()
        logger.exception("generation: bulk insert failed")
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

    df_gr = extract_generation("GR", start, end)
    load_generation(df_gr)
    load_generation(df_gr)

    df_de = extract_generation("DE_LU", start, end)
    load_generation(df_de)
    load_generation(df_de)

    logger.info(
        "Ran GR + DE_LU, 2x each. Check pgadmin: SELECT COUNT(*) FROM generation;"
    )