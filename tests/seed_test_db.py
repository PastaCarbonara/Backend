from core.db.models import *
from app.user.utils import get_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def seed_db():
    # we can now construct a Session() without needing to pass the
    # engine each time
    engine = create_engine("sqlite:///./test.db")

    # a sessionmaker(), also in the same scope as the engine
    Session = sessionmaker(engine)

    with Session() as session:
        image_1 = File(filename="image_1")
        image_2 = File(filename="image_2")
        image_3 = File(filename="image_3")
        image_4 = File(filename="image_4")
        
        admin = User(display_name="admin", is_admin=True, client_token=uuid.uuid4(), filename="image_4")
        admin.account_auth = AccountAuth(
            username="admin", password=get_password_hash("admin")
        )
        normal_user = User(display_name="normal_user", client_token=uuid.uuid4(), filename="image_4")
        normal_user.account_auth = AccountAuth(
            username="normal_user", password=get_password_hash("normal_user")
        )

        group_1 = Group(name="group_1", filename="image_3")
        group_1.users.append(GroupMember(user=admin, is_admin=True))

        group_2 = Group(name="group_2", filename="image_3")
        group_2.users.append(GroupMember(user=admin, is_admin=True))
        group_2.users.append(GroupMember(user=normal_user, is_admin=False))

        group_3 = Group(name="group_3", filename="image_3")
        group_3.users.append(GroupMember(user=admin, is_admin=True))

        # done like this because session.flush() did not work.
        # user id 1 should be admin, group id 1 and 2 should be group_1 and .._2 respectivly
        session_1 = SwipeSession(user_id=1, group_id=1)
        session_2 = SwipeSession(user_id=1, group_id=2)
        session_3 = SwipeSession(user_id=1, group_id=2)

        recipe_1 = Recipe(
            name="Union pie",
            description="The greatest union pie in the west.",
            instructions=[
                "Lay it down",
                "Slice it",
                "Cook it",
                "Wait for it to cool",
                "Add topping",
                "Enjoy",
            ],
            preparation_time=30,
            spiciness=0,
            filename="image_1",
            creator=admin,
        )

        recipe_2 = Recipe(
            name="Guacamole",
            description="Green sauce.",
            instructions=["Peel the avocado", "Peel the garlic", "Add ALL the pepper"],
            preparation_time=15,
            spiciness=0,
            filename="image_2",
            creator=admin,
        )
        tags = [Tag(name="tag1", tag_type="Keuken"), Tag(name="tag2", tag_type="Keuken"), Tag(name="tag3", tag_type="Keuken")]
        ingredients = [
            Ingredient(name="ingredient1"),
            Ingredient(name="ingredient2"),
            Ingredient(name="ingredient3"),
        ]

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
                image_1,
                image_2,
                image_3,
                image_4,
                recipe_1,
                recipe_2,
                *tags,
                *ingredients,
            ]
        )
        session.commit()

    # needed to call this because test.db couldnt be deleted anymore
    engine.dispose()
