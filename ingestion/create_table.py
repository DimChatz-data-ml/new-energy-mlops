from ingestion.db_connection import create_connection

CREATE_PRICES_TABLE = """
CREATE TABLE IF NOT EXISTS prices (
    "timestamp" TIMESTAMPTZ,
    prices numeric,
    country varchar(10),
    PRIMARY KEY ("timestamp", country)
);
"""
def create_prices_table():
    conn=create_connection()
    cur = conn.cursor()
    cur.execute(CREATE_PRICES_TABLE)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_prices_table()


