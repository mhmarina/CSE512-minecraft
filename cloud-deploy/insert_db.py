import os
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

#load credentials from .env file (i think this is good just so that the credentials are not in the code)
#.env file should be located in CSE512-MINECRAFT/.env
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME", "minecraft")

#getting SQL path
SQL_DIR = str(Path(__file__).resolve().parent  / "SQL Queries/")
#load sql files
with open(f"{SQL_DIR}/insert_servers.sql", "r") as f:
    sql_insert_server = f.read().strip()

with open(f"{SQL_DIR}/insert_server_data.sql", "r") as f:
    sql_insert_server_data = f.read().strip()


def insert_data(data_list):
    # {
    #     "ip": str,
    #     "timestamp": str,
    #     "online": bool,
    #     "latency": float, --> None if offline
    #     "curr_players": int, --> None if offline
    #     "max_players": int --> None if offline
    # }

    conn = psycopg2.connect(
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:26257/{DB_NAME}?sslmode=require"
    )
    cur = conn.cursor()

    try:
        # Insert into servers table
        execute_values(cur, sql_insert_server, [(d["ip"],) for d in data_list])

        # Insert into server_data table
        execute_values(cur, sql_insert_server_data, [
            (
                d["ip"],
                d["timestamp"],
                d["online"],
                d.get("latency", 0) or 0,
                d.get("curr_players", 0) or 0,
                d.get("max_players", 0) or 0
            )
            for d in data_list
        ])

        conn.commit()
        print(f"Inserted {len(data_list)} server records into CockroachDB")

    except Exception as e:
        conn.rollback()
        print(f"Error occured when inserting data to database : {e}")

    finally:
        cur.close()
        conn.close()
