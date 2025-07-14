import uuid
from app.database import execute_query

CATEGORY_ROWS = [
    "C",
    "C++",
    "DSA",
    "DBMS",
    "Computer Graphics",
    "Computer Networks",
    "Minor",
    "Major",
]
DEPARTMENT_ROWS = [
    "Electronics & Computer Engineering",
    "Automobile & Mechanical Engineering",
    "Civil Engineering",
    "Industrial Engineering",
    "Architecture",
    "Applied Sciences",
]
BATCH_YEARS = [2078, 2079, 2080, 2081]


def seed_lookup_tables():
    # Create Sample User
    user_query = f"""
    INSERT INTO "user" (
        uuid, username, first_name, last_name, phone_no, user_role,
        email, is_active, is_archived, date_joined, updated_at
    )
    VALUES (
        '{uuid.uuid4()}', 'admin', 'Bibek', 'Joshi', '9800000000', 'ADMIN',
        'admin@gmail.com', TRUE, FALSE, now(), now()
    )
    ON CONFLICT (username) DO NOTHING;
    """
    execute_query(user_query)

    execute_query(
        "INSERT INTO category (name) VALUES "
        + ",".join("(%s)" for _ in CATEGORY_ROWS)
        + " ON CONFLICT (name) DO NOTHING;",
        tuple(CATEGORY_ROWS),
    )
    execute_query(
        "INSERT INTO department (name) VALUES "
        + ",".join("(%s)" for _ in DEPARTMENT_ROWS)
        + " ON CONFLICT (name) DO NOTHING;",
        tuple(DEPARTMENT_ROWS),
    )
    execute_query(
        "INSERT INTO batch_year (year) VALUES "
        + ",".join("(%s)" for _ in BATCH_YEARS)
        + " ON CONFLICT (year) DO NOTHING;",
        tuple(BATCH_YEARS),
    )
