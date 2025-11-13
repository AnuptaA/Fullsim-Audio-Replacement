"""add likert questions

Revision ID: 8c3f7a1b2d4e
Revises: da5ea4448fdb
Create Date: 2025-11-13 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8c3f7a1b2d4e'
down_revision = 'da5ea4448fdb'
branch_labels = None
depends_on = None


def upgrade():
    # ### add four Likert scale columns (1-5 ratings)
    with op.batch_alter_table('snippet_responses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('likert_mental_demand', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('likert_tone_difficulty', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('likert_confidence_conversation', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('likert_nonlexical_preserved', sa.Integer(), nullable=True))


def downgrade():
    # ### remove Likert columns
    with op.batch_alter_table('snippet_responses', schema=None) as batch_op:
        batch_op.drop_column('likert_nonlexical_preserved')
        batch_op.drop_column('likert_confidence_conversation')
        batch_op.drop_column('likert_tone_difficulty')
        batch_op.drop_column('likert_mental_demand')