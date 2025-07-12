"""project_discussion

Revision ID: eeecf725961c
Revises: e674958ba9fc
Create Date: 2025-07-12 13:02:46.927872

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "eeecf725961c"
down_revision: Union[str, Sequence[str], None] = "e674958ba9fc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create project_rating table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS project_rating (
            id BIGSERIAL PRIMARY KEY,
            project_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            rating SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE(project_id, user_id),
            CONSTRAINT fk_project_rating_project FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
            CONSTRAINT fk_project_rating_user FOREIGN KEY(user_id) REFERENCES "user"(id) ON DELETE CASCADE
        );
        """
    )

    # Create project_discussion table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS project_discussion (
            id BIGSERIAL PRIMARY KEY,
            project_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            comment TEXT NOT NULL,
            parent_id BIGINT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT fk_project_discussion_project FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
            CONSTRAINT fk_project_discussion_user FOREIGN KEY(user_id) REFERENCES "user"(id) ON DELETE CASCADE,
            CONSTRAINT fk_project_discussion_parent FOREIGN KEY(parent_id) REFERENCES project_discussion(id) ON DELETE SET NULL,
            CONSTRAINT chk_parent_not_self CHECK (id <> parent_id)
        );
        """
    )

    # Indexes for faster queries
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_rating_project ON project_rating(project_id);"
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_rating_user ON project_rating(user_id);")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_discussion_project ON project_discussion(project_id);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_discussion_user ON project_discussion(user_id);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_discussion_created_at ON project_discussion(created_at DESC);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_rating_created_at ON project_rating(created_at DESC);"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_discussion_created_at;")
    op.execute("DROP INDEX IF EXISTS idx_discussion_user;")
    op.execute("DROP INDEX IF EXISTS idx_discussion_project;")
    op.execute("DROP INDEX IF EXISTS idx_rating_created_at;")
    op.execute("DROP INDEX IF EXISTS idx_rating_user;")
    op.execute("DROP INDEX IF EXISTS idx_rating_project;")
    op.execute("DROP TABLE IF EXISTS project_discussion;")
    op.execute("DROP TABLE IF EXISTS project_rating;")
