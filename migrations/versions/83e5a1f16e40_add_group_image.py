"""Add group image

Revision ID: 83e5a1f16e40
Revises: 586f256b6080
Create Date: 2023-04-13 10:18:53.004023

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83e5a1f16e40'
down_revision = '586f256b6080'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    print(op.get_context().dialect.name)
    if op.get_context().dialect.name == "sqlite":
        with op.batch_alter_table('group') as batch_op:
            batch_op.add_column(sa.Column('filename', sa.String(), nullable=False))
            batch_op.create_foreign_key('group_file', 'file', ['filename'], ['filename'], ondelete='CASCADE')

    else:
        op.add_column('group', sa.Column('filename', sa.String(), nullable=False))
        op.create_foreign_key(None, 'group', 'file', ['filename'], ['filename'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'group', type_='foreignkey')
    op.drop_column('group', 'filename')
    # ### end Alembic commands ###
