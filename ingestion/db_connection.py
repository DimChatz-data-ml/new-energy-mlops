import os
import psycopg2

def create_connection():
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
    )
    return conn