"""add user_verification table

Revision ID: 50e85cd9513a
Revises: 1b793fdbe5dc
Create Date: 2025-07-09 14:55:55.916994

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "50e85cd9513a"
down_revision: Union[str, Sequence[str], None] = "1b793fdbe5dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE user_verification (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            otp VARCHAR(6) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT fk_user_verification_user FOREIGN KEY(user_id) REFERENCES "user"(id) ON DELETE CASCADE
        );
        CREATE INDEX idx_user_verification_user_id ON user_verification(user_id);
    """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_user_verification_user_id;")
    op.execute("DROP TABLE IF EXISTS user_verification;")
