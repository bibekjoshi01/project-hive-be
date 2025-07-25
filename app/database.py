from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import Optional, Any, Tuple
from psycopg2.extras import RealDictCursor

from .config import settings

DATABASE_URL = settings.database_url

db_pool = pool.SimpleConnectionPool(
    minconn=1, maxconn=10, dsn=DATABASE_URL, cursor_factory=RealDictCursor
)


def get_connection():
    return db_pool.getconn()


def put_connection(conn):
    db_pool.putconn(conn)


def perform_query(query: str, params: tuple = (), conn=None):
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, params)
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        if close_after:
            put_connection(conn)


def execute_query(
    query: str, params: Optional[Tuple] = None, conn=None
) -> Optional[Any]:
    """
    Execute an INSERT/UPDATE/DELETE query.

    If the query includes a RETURNING clause, returns the first column of the first row.
    Otherwise returns None.

    Args:
        query (str): SQL query to execute, possibly with placeholders (%s).
        params (tuple, optional): parameters for the query.

    Returns:
        Optional[Any]: Returned value from RETURNING clause or None.
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, params or ())
        result = None
        if cur.description:
            row = cur.fetchone()
            if row:
                result = row
        conn.commit()
        return result
    finally:
        cur.close()
        if close_after:
            put_connection(conn)
