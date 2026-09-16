from ingestion.db_connection import create_connection

CREATE_PRICES_TABLE = """
CREATE TABLE IF NOT EXISTS prices (
    "timestamp" TIMESTAMPTZ,
    price numeric,
    country varchar(10),
    PRIMARY KEY ("timestamp", country)
);
"""
CREATE_LOAD_TABLE= """

CREATE TABLE IF NOT EXISTS LOAD(
    "timestamp" TIMESTAMPTZ,
    actual_load numeric,
    country varchar(10),
    PRIMARY KEY ("timestamp", country)
);
"""


CREATE_GENERATION_TABLE= """

CREATE TABLE IF NOT EXISTS GENERATION(
    "timestamp" TIMESTAMPTZ,
    production_type varchar(100),
    country varchar(10),
    quantity_mw numeric,
    PRIMARY KEY ("timestamp",country,production_type)
);
"""




CREATE_WIND_SOLAR_TABLE= """

CREATE TABLE IF NOT EXISTS WIND_SOLAR(
    "timestamp" TIMESTAMPTZ,
    production_type varchar(50),
    country varchar(10),
    forecast_mw numeric,
    PRIMARY KEY ("timestamp",country,production_type)
);
"""






def create_all_tables():
    conn=create_connection()
    cur = conn.cursor()

    cur.execute(CREATE_PRICES_TABLE)
    cur.execute(CREATE_LOAD_TABLE)
    cur.execute(CREATE_GENERATION_TABLE)
    cur.execute(CREATE_WIND_SOLAR_TABLE)


    conn.commit()
    cur.close()
    conn.close()
    print(' All tables created successfully! ')

if __name__ == "__main__":
    create_all_tables()


