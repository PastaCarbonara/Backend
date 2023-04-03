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
        session.add_all([admin, normal_user])
        session.commit()

    # needed to call this because test.db couldnt be deleted anymore
    engine.dispose()
