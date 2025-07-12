from typing import Sequence, Union
from alembic import op

revision: str = '1b793fdbe5dc'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Create `user` table without foreign keys
    op.execute("""
        CREATE TABLE "user" (
            id BIGSERIAL PRIMARY KEY,
            uuid UUID NOT NULL UNIQUE,
            username VARCHAR(150) NOT NULL UNIQUE,
            first_name VARCHAR(150) NOT NULL,
            last_name VARCHAR(150) NOT NULL,
            phone_no VARCHAR(15) NOT NULL,
            email VARCHAR(254) NOT NULL,
            photo VARCHAR(500),
            password VARCHAR(128),
            last_login TIMESTAMPTZ,
            is_active BOOLEAN NOT NULL,
            is_archived BOOLEAN NOT NULL,
            date_joined TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL,
            user_role VARCHAR(100) NOT NULL CHECK (user_role IN ('VISITOR', 'ADMIN', 'STAFF'))
        );
        CREATE UNIQUE INDEX unique_email_active_user ON "user" (email) WHERE NOT is_archived;
        CREATE INDEX user_username_like ON "user" (username varchar_pattern_ops);
    """)


def downgrade() -> None:
    op.execute('DROP TABLE IF EXISTS "user" CASCADE;')
