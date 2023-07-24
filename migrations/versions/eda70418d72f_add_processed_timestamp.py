# pylint: skip-file
"""add processed timestamp

Revision ID: eda70418d72f
Revises: 0c6ba8e267b2
Create Date: 2021-10-14 17:57:44.623274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eda70418d72f'
down_revision = '0c6ba8e267b2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('history',
        sa.Column('processed_timestamp', sa.DateTime(timezone=True))
    )


def downgrade():
    op.drop_column('history', 'processed_timestamp')
