import uuid
from app.database import execute_query


CATEGORY_ROWS = [
    "C Programming",
    "C++ (OOP)",
    "DSA",
    "DBMS",
    "Computer Graphics",
    "Computer Networks",
    "Data Mining",
    "Image Processing",
    "AI",
    "Minor",
    "Major",
]
DEPARTMENT_ROWS = [
    "Electronics Engineering",
    "Computer Engineering",
    "Automobile Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Industrial Engineering",
    "Architecture",
    "Applied Sciences",
]
BATCH_YEARS = [2076, 2077, 2078, 2079, 2080, 2081, 2082]


def seed_lookup_tables():
    # Create Admin User
    user_query = f"""
    INSERT INTO "user" (
        uuid, username, first_name, last_name, phone_no, user_role,
        email, is_active, is_archived, date_joined, updated_at
    )
    VALUES (
        '{uuid.uuid4()}', 'admin', 'Admin', 'Admin', '9800000000', 'ADMIN',
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
