"""cascade recipe ingredient

Revision ID: 4e1648340105
Revises: 88d8c5240c07
Create Date: 2023-05-10 13:10:37.810274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e1648340105'
down_revision = '88d8c5240c07'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('recipe_ingredient_ingredient_id_fkey', 'recipe_ingredient', type_='foreignkey')
    op.create_foreign_key(None, 'recipe_ingredient', 'ingredient', ['ingredient_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'recipe_ingredient', type_='foreignkey')
    op.create_foreign_key('recipe_ingredient_ingredient_id_fkey', 'recipe_ingredient', 'ingredient', ['ingredient_id'], ['id'])
    # ### end Alembic commands ###
