import os
import psycopg2

def main():
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print("Connected! Postgres version:", cur.fetchone())
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()