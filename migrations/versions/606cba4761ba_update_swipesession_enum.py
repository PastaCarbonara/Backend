"""update swipesession enum

Revision ID: 606cba4761ba
Revises: 1d6b849f8442
Create Date: 2023-04-04 13:03:40.324713

"""
from alembic import op
import sqlalchemy as sa

from core.db.models import SwipeSession


# revision identifiers, used by Alembic.
revision = '606cba4761ba'
down_revision = '1d6b849f8442'
branch_labels = None
depends_on = None

old_options = ('Gepauzeerd', 'Gestopt', 'Is bezig', 'Voltooid')
new_options = sorted(old_options + ('Staat klaar',))

old_type = sa.Enum(*old_options, name='swipesessionenum')
new_type = sa.Enum(*new_options, name='swipesessionenum')
tmp_type = sa.Enum(*new_options, name='_swipesessionenum')


def upgrade():
    
    if op.get_bind().dialect.name.startswith('sqlite'):
        with op.batch_alter_table('swipe_session') as batch_op:
            # we are expecting the test sqlite database not to exist, 
            # so we dont care about maintaining the values of previous entries 
            # (as all tables are empty anyway)
            batch_op.alter_column('status',
                existing_type=sa.Enum('Gepauzeerd', 'Gestopt', 'Is bezig', 'Voltooid', 'Staat klaar', name='swipesessionenum'),
                nullable=False,
                server_default='Staat klaar',
                postgresql_using='status::text::swipesessionenum'
            )

    else:
        # Create a tempoary "_status" type, convert and drop the "old" type
        tmp_type.create(op.get_bind(), checkfirst=False)
        op.alter_column('swipe_session', 'status', type_=tmp_type, postgresql_using='status::text::_swipesessionenum')
        old_type.drop(op.get_bind(), checkfirst=False)

        # Create and convert to the "new" status type
        new_type.create(op.get_bind(), checkfirst=False)
        op.alter_column('swipe_session', 'status', type_=new_type, postgresql_using='status::text::swipesessionenum')
        tmp_type.drop(op.get_bind(), checkfirst=False)

def downgrade():
    # Convert 'Staat klaar' status into 'Gepauzeerd'
    op.execute(
        sa.text(
            f"UPDATE swipe_session SET status = 'Is bezig' "
            f"WHERE status = 'Staat klaar'"
        ),
    )
    # Create a temporary "_status" type, convert and drop the "new" type
    tmp_type.create(op.get_bind(), checkfirst=False)
    op.alter_column('swipe_session', 'status', type_=tmp_type, postgresql_using='status::text::_swipesessionenum')
    new_type.drop(op.get_bind(), checkfirst=False)
    # Create and convert to the "old" status type
    old_type.create(op.get_bind(), checkfirst=False)
    op.alter_column('swipe_session', 'status', type_=old_type, postgresql_using='status::text::swipesessionenum')
    tmp_type.drop(op.get_bind(), checkfirst=False)
