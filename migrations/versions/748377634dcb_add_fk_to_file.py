"""add fk to file

Revision ID: 748377634dcb
Revises: ebe4a1c77841
Create Date: 2023-06-25 11:30:35.920842

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "748377634dcb"
down_revision = "ebe4a1c77841"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # add user_id column to file

    op.add_column("file", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "file", "user", ["user_id"], ["id"], ondelete="CASCADE")

    # Update existing rows to set a non-null value for user_id
    op.execute("UPDATE file SET user_id = 1 WHERE user_id IS NULL")

    # Modify the column to be NOT NULL
    op.alter_column("file", "user_id", nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "file", type_="foreignkey")
    op.drop_column("file", "user_id")
    # ### end Alembic commands ###
