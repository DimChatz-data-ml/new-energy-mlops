import polars as pl
from ingestion.db_connection import create_connection


def  read_table(table_name):
    conn=create_connection()
    df = pl.read_database(query=f"SELECT * FROM {table_name}", connection=conn)    
    conn.close()
    return df

def check_resolution(df):
    df=df.sort("timestamp").with_columns(pl.col('timestamp').diff().alias('time_diff'))
    return df


if __name__ == "__main__":
    df = read_table("prices")
    df = check_resolution(df)
    print(df["time_diff"].unique())