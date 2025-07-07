from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from .config import settings

DATABASE_URL = settings.database_url

db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL,
    cursor_factory=RealDictCursor
)

def get_connection():
    return db_pool.getconn()

def put_connection(conn):
    db_pool.putconn(conn)

def perform_query(query: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        put_connection(conn)