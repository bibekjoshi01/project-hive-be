"""newsletter_contact_us

Revision ID: cafbbab3aea4
Revises: 50e85cd9513a
Create Date: 2025-07-12 11:35:00.138925

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "cafbbab3aea4"
down_revision: Union[str, Sequence[str], None] = "50e85cd9513a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NEWSLETTER_SQL = """
CREATE TABLE IF NOT EXISTS newsletter_subscriber (
    id            BIGSERIAL PRIMARY KEY,
    email         VARCHAR(254) NOT NULL UNIQUE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);
"""

CONTACT_SQL = """
CREATE TABLE IF NOT EXISTS contact_message (
    id            BIGSERIAL PRIMARY KEY,
    full_name     VARCHAR(120) NOT NULL,
    email         VARCHAR(254) NOT NULL,
    phone_no      VARCHAR(20),
    subject       VARCHAR(200),
    message       TEXT         NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_contact_created_at
          ON contact_message (created_at DESC);
"""


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(NEWSLETTER_SQL)
    op.execute(CONTACT_SQL)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS contact_message;")
    op.execute("DROP TABLE IF EXISTS newsletter_subscriber;")
