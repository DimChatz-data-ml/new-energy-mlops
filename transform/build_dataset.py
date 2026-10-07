import polars as pl
from dotenv import load_dotenv

from ingestion.db_connection import create_connection


def build_prices(connection):
    query = "select timestamp, price, country from prices"
    df = pl.read_database(query=query, connection=connection)

    # sort is required: group_by_dynamic fails with "input data is not sorted" otherwise
    return (
        df.sort(["country", "timestamp"])
        .group_by_dynamic(
            index_column="timestamp",
            every="1h",
            group_by=["country"],
        )
        .agg(
            pl.col("price").mean().alias("avg_price"),
            pl.len().alias("n"),
        )
        # row order after the group_by is not guaranteed
        .sort(["country", "timestamp"])
    )


if __name__ == "__main__":
    load_dotenv()
    connection = create_connection()

    df = build_prices(connection)
    print(df.shape)
    print(df.head(5))
    print(df.tail(5))
    print(df.schema)
    print(df.group_by("n").len())
    print(df.null_count())