from core.db.models import *
from app.user.services import UserService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def seed_db():
    # we can now construct a Session() without needing to pass the
    # engine each time
    engine = create_engine("sqlite:///./test.db")

    # a sessionmaker(), also in the same scope as the engine
    Session = sessionmaker(engine)

    service = UserService()

    with Session() as session:
        admin = User()
        admin.profile = UserProfile(
            username="admin", password=service.get_password_hash("admin"), is_admin=True
        )
        normal_user = User()
        normal_user.profile = UserProfile(
            username="normal_user", password=service.get_password_hash("normal_user")
        )

        group_1 = Group(name="group_1")
        group_1.users.append(GroupMember(user=admin, is_admin=True))

        group_2 = Group(name="group_2")
        group_2.users.append(GroupMember(user=admin, is_admin=True))
        group_2.users.append(GroupMember(user=normal_user, is_admin=False))

        group_3 = Group(name="group_3")
        group_3.users.append(GroupMember(user=admin, is_admin=True))

        # done like this because session.flush() did not work.
        # user id 1 should be admin, group id 1 and 2 should be group_1 and .._2 respectivly
        session_1 = SwipeSession(user_id=1, group_id=1)
        session_2 = SwipeSession(user_id=1, group_id=2)
        session_3 = SwipeSession(user_id=1, group_id=2)

        session.add_all(
            [
                admin,
                normal_user,
                group_1,
                group_2,
                group_3,
                session_1,
                session_2,
                session_3,
            ]
        )
        session.commit()

    # needed to call this because test.db couldnt be deleted anymore
    engine.dispose()
