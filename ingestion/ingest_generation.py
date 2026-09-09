from ingestion.api_connection import api_con_func
from ingestion.db_connection import create_connection
import pandas as pd


def extract_generation(country, start, end):
    client = api_con_func()
    df = client.query_generation(country, start=start, end=end)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()
    df = df.rename(columns={'index': 'timestamp'})
    df = df.melt(id_vars=['timestamp'], var_name='production_type', value_name='quantity_mw')
    df['country'] = country

    return df


def load_generation(df):
    connection = create_connection()
    cursor = connection.cursor()
    counter = 0
    for index, row in df.iterrows():
        try:
            cursor.execute(
        """INSERT INTO generation (timestamp, production_type, quantity_mw, country) 
        VALUES (%s, %s, %s, %s) 
        ON CONFLICT (timestamp, country, production_type) 
        DO UPDATE SET quantity_mw = EXCLUDED.quantity_mw""",
        (row['timestamp'], row['production_type'], row['quantity_mw'], row['country']))
            counter += 1
            if counter == 500:
                connection.commit()
                counter = 0

        except Exception as e:
            connection.rollback()
            print(f'problem {e} in index {index}')

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    end = pd.Timestamp.now(tz="Europe/Athens")
    start = end - pd.Timedelta(days=2)

    df = extract_generation("GR", start, end)
    load_generation(df)      # 1st time
    load_generation(df)      # 2nd time

    print("It ran 2 times.Check pgadmin: SELECT COUNT(*) FROM generation;")