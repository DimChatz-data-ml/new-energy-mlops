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
            pl.len().alias("n_prices"),
        )
        # row order after the group_by is not guaranteed
        .sort(["country", "timestamp"])
    )


def build_load(connection):
    query="select timestamp,actual_load,country from load"
    df=pl.read_database(query=query,connection=connection)

    return(

        df.sort(['country','timestamp'])
        .group_by_dynamic(
            index_column='timestamp',
            every='1h',
            group_by=['country']       
        )
        .agg(
            pl.col('actual_load').mean().alias('avg_load'),
            pl.len().alias('n_load')
        )
        .sort(['country','timestamp'])
        # group_by_dynamic creates no row for an hour with zero measurements,
        # so those hours would silently vanish. upsample adds one row per
        # missing hour (nulls in avg_load and n_load), so the table has
        # exactly one row per hour per country. Without this, shift(24)
        # for lag features would no longer mean "24 hours ago".
        .upsample(time_column='timestamp', every='1h', group_by='country')
        .sort(['country', 'timestamp'])
        )

def build_generation(connection):
    query = "select timestamp, production_type, country, quantity_mw from generation"
    df = pl.read_database(query=query, connection=connection)
    out=(
        df.filter(
            ~pl.col("production_type").str.ends_with("Consumption"))
            .with_columns(pl.col('production_type').str.strip_suffix(" - Actual Aggregated"))
        )
    return out



if __name__ == "__main__":
    load_dotenv()
    connection = create_connection()

    prices_df = build_prices(connection)
    print(prices_df.shape)
    print(prices_df.head(5))
    print(prices_df.tail(5))
    print(prices_df.schema)
    print(prices_df.group_by("n_prices").len())
    print(prices_df.null_count())

    load_df = build_load(connection)
    print(load_df.shape)
    print(load_df.head(5))
    print(load_df.tail(5))
    print(load_df.schema)
    print(load_df.group_by("n_load").len())
    print(load_df.null_count())
    print(load_df.group_by("country").len().sort("country"))