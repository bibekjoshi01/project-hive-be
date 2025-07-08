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
            photo VARCHAR(100),
            password VARCHAR(128),
            last_login TIMESTAMPTZ,
            is_active BOOLEAN NOT NULL,
            is_archived BOOLEAN NOT NULL,
            date_joined TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL,
            created_by_id BIGINT,
            updated_by_id BIGINT,
            user_role_id BIGINT NOT NULL
        );
        CREATE UNIQUE INDEX unique_email_active_user ON "user" (email) WHERE NOT is_archived;
        CREATE INDEX user_created_by_idx ON "user" (created_by_id);
        CREATE INDEX user_updated_by_idx ON "user" (updated_by_id);
        CREATE INDEX user_username_like ON "user" (username varchar_pattern_ops);
    """)

    # Step 2: Create `user_role` table
    op.execute("""
        CREATE TABLE user_role (
            id BIGSERIAL PRIMARY KEY,
            uuid UUID NOT NULL UNIQUE,
            created_at TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL,
            is_active BOOLEAN NOT NULL,
            is_archived BOOLEAN NOT NULL,
            name VARCHAR(50) NOT NULL UNIQUE,
            codename VARCHAR(50) NOT NULL UNIQUE,
            created_by_id BIGINT NOT NULL,
            updated_by_id BIGINT
        );
        CREATE INDEX user_role_codename_like ON user_role (codename varchar_pattern_ops);
        CREATE INDEX user_role_name_like ON user_role (name varchar_pattern_ops);
        CREATE INDEX user_role_created_by_idx ON user_role (created_by_id);
        CREATE INDEX user_role_updated_by_idx ON user_role (updated_by_id);
    """)

    # Step 3: Add foreign keys now that both tables exist
    op.execute("""
        ALTER TABLE "user" ADD CONSTRAINT user_created_by_id_fk FOREIGN KEY (created_by_id) REFERENCES "user"(id) DEFERRABLE INITIALLY DEFERRED;
        ALTER TABLE "user" ADD CONSTRAINT user_updated_by_id_fk FOREIGN KEY (updated_by_id) REFERENCES "user"(id) DEFERRABLE INITIALLY DEFERRED;
        ALTER TABLE "user" ADD CONSTRAINT user_user_role_id_fk FOREIGN KEY (user_role_id) REFERENCES user_role(id) DEFERRABLE INITIALLY DEFERRED;

        ALTER TABLE user_role ADD CONSTRAINT user_role_created_by_id_fk FOREIGN KEY (created_by_id) REFERENCES "user"(id) DEFERRABLE INITIALLY DEFERRED;
        ALTER TABLE user_role ADD CONSTRAINT user_role_updated_by_id_fk FOREIGN KEY (updated_by_id) REFERENCES "user"(id) DEFERRABLE INITIALLY DEFERRED;
    """)


def downgrade() -> None:
    op.execute('DROP TABLE IF EXISTS "user" CASCADE;')
    op.execute('DROP TABLE IF EXISTS user_role CASCADE;')
