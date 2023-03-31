from sqlalchemy import or_, select, and_

from core.db import Transactional, session
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
        user = User()
        session.add(user)
        user.profile = UserProfile(
            username="admin", password=service.get_password_hash("admin"), is_admin=True
        )
        session.add(user)
        session.commit()
    # closes the session
