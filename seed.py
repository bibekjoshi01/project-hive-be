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
PROJECT_SEEDS = [
    (
        "Smart Irrigation System",
        "-",
        "IoT-based automated irrigation controller",
        2,
        2,
        1,
        "Bachelors",
        "Dr. A. Sharma",
        "LoRa, ESP32, Django, React",
        "https://github.com/example/smart-irrigation",
        None,
        "APPROVED",
        1,
        1,
    ),
    (
        "Voice-controlled Wheelchair",
        "-",
        "Wheelchair that moves with voice commands",
        1,
        3,
        1,
        "Bachelors",
        "Prof. B. Khadka",
        "Arduino, Python, Speech-to-Text",
        None,
        None,
        "PENDING",
        1,
        1,
    ),
]


new_project_seeds = []
for row in PROJECT_SEEDS:
    slug = str(uuid.uuid4())
    new_row = list(row)
    new_row.insert(2, slug)
    new_project_seeds.append(tuple(new_row))


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
    execute_query(
        "INSERT INTO project ("
        "  title, project_details, slug, abstract, batch_year_id, category_id, department_id, "
        "  level, supervisor, technologies_used, github_link, "
        "  documentation_link, status, submitted_by, approved_by"
        ") VALUES "
        + ",".join("(" + ",".join(["%s"] * 15) + ")" for _ in new_project_seeds)
        + ";",
        tuple(value for row in new_project_seeds for value in row),
    )
