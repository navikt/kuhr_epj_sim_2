import os
import oracledb
from dotenv import load_dotenv
from typing import Optional


load_dotenv()


def startup_pool() -> oracledb.ConnectionPool:
    print("Creating database connection pool...")
    try:
        pool: oracledb.ConnectionPool = oracledb.create_pool(
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            dsn=os.getenv("THIN"),
            min=2,
            max=5,
            increment=1
        )
        print("Connection pool created successfully.")
        return pool
    except oracledb.Error as e:
        print("Error creating database connection pool:", e)
        raise


def get_connection(pool: oracledb.ConnectionPool) -> oracledb.Connection:
    conn: Optional[oracledb.Connection] = None
    try:
        conn = pool.acquire()
        print(f"Acquired connection from pool ({pool.opened}/{pool.max})")
        return conn
    except oracledb.Error as e:
        print("Error acquiring connection:", e)
        raise
