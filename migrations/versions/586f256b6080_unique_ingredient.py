"""unique ingredient

Revision ID: 586f256b6080
Revises: ac2288fcfdb9
Create Date: 2023-04-07 14:55:23.621548

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "586f256b6080"
down_revision = "ac2288fcfdb9"
branch_labels = None
depends_on = None


def upgrade():
    if op.get_context().dialect.name == "postgresql":
        op.create_unique_constraint(None, "ingredient", ["name"])
    else:
        # create new table with unique constraint
        op.create_table(
            "ingredient_new",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint("id", name="pk_ingredient_new"),
            sa.UniqueConstraint("name", name="uq_ingredient_new_name"),
        )

        # copy data from old table to new table
        op.execute(
            "INSERT INTO ingredient_new (id, name) SELECT id, name FROM ingredient"
        )

        # drop old table and rename new table
        op.drop_table("ingredient")
        op.rename_table("ingredient_new", "ingredient")


def downgrade():
    if op.get_context().dialect.name == "postgresql":
        op.drop_constraint(None, "ingredient", type_="unique")
    else:
        # create new table without unique constraint
        op.create_table(
            "ingredient_new",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=50), nullable=False),
            sa.PrimaryKeyConstraint("id", name="pk_ingredient_new"),
        )

        # copy data from old table to new table
        op.execute(
            "INSERT INTO ingredient_new (id, name) SELECT id, name FROM ingredient"
        )

        # drop old table and rename new table
        op.drop_table("ingredient")
        op.rename_table("ingredient_new", "ingredient")
