# pylint: skip-file
"""create history table

Revision ID: 9375164b3f2f
Revises: 
Create Date: 2021-09-15 15:26:10.758002

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as postgres


# revision identifiers, used by Alembic.
revision = '9375164b3f2f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'history',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('request', postgres.JSONB, nullable=False),
        sa.Column('email_content', postgres.JSONB),
        sa.Column('result', sa.TEXT),
        sa.Column('date_created', sa.DateTime(timezone=True))
    )


def downgrade():
    op.drop_table('history')
