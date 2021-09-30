# pylint: skip-file
"""set date_created default

Revision ID: 0c6ba8e267b2
Revises: 9375164b3f2f
Create Date: 2021-09-29 17:26:36.531981

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as postgres
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '0c6ba8e267b2'
down_revision = '9375164b3f2f'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('history', 'date_created', server_default=func.now())


def downgrade():
    pass
