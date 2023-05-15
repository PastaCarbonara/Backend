"""add type to tag

Revision ID: 88d8c5240c07
Revises: 6cf9020bb738
Create Date: 2023-05-10 10:24:28.710975

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88d8c5240c07'
down_revision = '6cf9020bb738'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    tag_type_choices = ('Allergieën', 'Keuken', 'Dieet')

    if op.get_context().dialect.name == 'postgresql':
        tag_type_enum = postgresql.ENUM(*tag_type_choices, name='tagtype')
        tag_type_enum.create(op.get_bind(), checkfirst=True)
        tag_type = tag_type_enum
    else:
        tag_type = sa.String(length=50)

    op.add_column('tag', sa.Column('tag_type', tag_type, nullable=False, server_default=tag_type_choices[0]))
    op.execute("UPDATE tag SET tag_type = 'Allergieën'")

    if op.get_context().dialect.name == 'sqlite':
        op.create_check_constraint('tag_type_choices', 'tag', sa.sql.column('tag_type').in_(tag_type_choices))

def downgrade():
    op.drop_column('tag', 'tag_type')
    if op.get_context().dialect.name == 'postgresql':
        postgresql.ENUM(name='tagtype').drop(op.get_bind(), checkfirst=True)
    elif op.get_context().dialect.name == 'sqlite':
        op.drop_constraint('tag_type_choices', 'tag', type_='check')

