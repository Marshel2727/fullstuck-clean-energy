"""Transactional cache namespaces; does not modify business data."""
from alembic import op
import sqlalchemy as sa

revision = "0002_cache_epochs"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("cache_epochs",
        sa.Column("namespace", sa.String(100), primary_key=True),
        sa.Column("revision", sa.String(32), nullable=False),
        mysql_engine="InnoDB", mysql_charset="utf8mb4", mysql_collate="utf8mb4_unicode_ci")


def downgrade():
    op.drop_table("cache_epochs")
