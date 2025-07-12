"""project

Revision ID: e674958ba9fc
Revises: cafbbab3aea4
Create Date: 2025-07-12 12:31:48.535033

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e674958ba9fc"
down_revision: Union[str, Sequence[str], None] = "cafbbab3aea4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create category table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS category (
            id BIGSERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        );
    """
    )

    # Create department table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS department (
            id BIGSERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        );
    """
    )

    # Create batch_year table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS batch_year (
            id BIGSERIAL PRIMARY KEY,
            year INTEGER UNIQUE NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        );
    """
    )

    # Create enum type for project level
    op.execute(
        """
        CREATE TYPE project_level_enum AS ENUM ('Masters', 'Bachelors', 'PHD');
    """
    )
    op.execute(
        """
        CREATE TYPE project_status_enum AS ENUM ('PENDING', 'APPROVED', 'REJECTED');
    """
    )

    # Create project table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS project (
            id BIGSERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            abstract VARCHAR(300) NOT NULL,
            batch_year_id BIGINT NOT NULL REFERENCES batch_year(id) ON DELETE CASCADE,
            category_id BIGINT NOT NULL REFERENCES category(id) ON DELETE CASCADE,
            department_id BIGINT NOT NULL REFERENCES department(id) ON DELETE CASCADE,
            level project_level_enum NOT NULL,
            supervisor VARCHAR(255) NOT NULL,
            project_details TEXT NOT NULL,
            technologies_used VARCHAR(1000) NOT NULL,
            github_link VARCHAR(1000),
            documentation_link VARCHAR(1000),
            status project_status_enum NOT NULL DEFAULT 'PENDING',
            submitted_by BIGINT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
            submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            approved_by BIGINT NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        );
    """
    )

    # Create project_team_member table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS project_team_member (
            id BIGSERIAL PRIMARY KEY,
            project_id BIGINT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
            full_name VARCHAR(255) NOT NULL,
            roll_no VARCHAR(50) NOT NULL,
            photo VARCHAR(255)
        );
    """
    )

    # Create project_files table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS project_files (
            id BIGSERIAL PRIMARY KEY,
            project_id BIGINT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
            file_type VARCHAR(100) NOT NULL,
            file VARCHAR(255) NOT NULL
        );
    """
    )

    # ----- indexes -----
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_project_category ON project(category_id);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_project_department ON project(department_id);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_project_batch_year ON project(batch_year_id);"
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_project_level ON project(level);")

    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_team_member_project ON project_team_member(project_id);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_project_files_project ON project_files(project_id);"
    )

    # Additional Constraints
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uniq_member_roll_per_project ON project_team_member(project_id, roll_no);"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS uniq_member_roll_per_project;")
    op.execute("DROP INDEX IF EXISTS idx_project_files_project;")
    op.execute("DROP INDEX IF EXISTS idx_team_member_project;")
    op.execute("DROP INDEX IF EXISTS idx_project_level;")
    op.execute("DROP INDEX IF EXISTS idx_project_batch_year;")
    op.execute("DROP INDEX IF EXISTS idx_project_department;")
    op.execute("DROP INDEX IF EXISTS idx_project_category;")

    op.execute("DROP TABLE IF EXISTS project_files;")
    op.execute("DROP TABLE IF EXISTS project_team_member;")
    op.execute("DROP TABLE IF EXISTS project;")
    op.execute("DROP TYPE IF EXISTS project_level_enum;")
    op.execute("DROP TYPE IF EXISTS project_status_enum;")
    op.execute("DROP TABLE IF EXISTS batch_year;")
    op.execute("DROP TABLE IF EXISTS department;")
    op.execute("DROP TABLE IF EXISTS category;")
