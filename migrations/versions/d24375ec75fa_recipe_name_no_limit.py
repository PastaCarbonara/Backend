"""recipe name no limit

Revision ID: d24375ec75fa
Revises: 3b0647ef8e61
Create Date: 2023-05-18 23:59:23.133630

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd24375ec75fa'
down_revision = '3b0647ef8e61'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'user', 'file', ['filename'], ['filename'], ondelete='CASCADE')
    op.alter_column('recipe', 'name',
               existing_type=sa.String(length=50, collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sa.String(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('table1', 'description',
               existing_type=sa.String(),
               type_=sa.String(length=50, collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=True)
    op.drop_constraint('user_filename_fkey', 'user', type_='foreignkey')
    # ### end Alembic commands ###
