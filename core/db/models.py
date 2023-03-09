
from email.policy import default
from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    Text,
    ForeignKey,
    Boolean,
    Table,
    JSON,
)

import sqlalchemy
from sqlalchemy.orm import relationship, Mapped, mapped_column

from core.db import Base
from core.db.mixins import TimestampMixin
from core.db.enums import SwipeSessionEnum


recipe_judgement = Table(
    "recipe_judgement",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipe.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("like", Boolean, default=False),
)


class User(Base, TimestampMixin):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    profile = relationship("UserProfile", backref="user")

    recipes = relationship("Recipe", backref="creator")
    judged_recipes = relationship("Recipe", secondary=recipe_judgement, backref="users")

    def __repr__(self):
        return f"{self.username} {self.id}"


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profile"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)

    # user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)

    username = Column(String(50), nullable=False)
    password = Column(Text, nullable=False)
    is_admin = Column(Boolean, default=False)


recipe_ingredient = Table(
    "recipe_ingredient",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipe.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "ingredient_id",
        ForeignKey("ingredient.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("amount", Float),
    Column("unit_id", ForeignKey("unit.id", ondelete="CASCADE")),
)

recipe_tag = Table(
    "recipe_tag",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipe.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
)


class Recipe(Base, TimestampMixin):
    __tablename__ = "recipe"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    instructions = Column(JSON, nullable=False)
    ingredients = relationship(
        "Ingredient", secondary=recipe_ingredient, backref="recipes"
    )
    tags = relationship("Tag", secondary=recipe_tag, backref="recipes")

    creator_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    preparing_time = Column(Integer)
    image = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return self.name


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)


class Ingredient(Base):
    __tablename__ = "ingredient"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


class Unit(Base):
    __tablename__ = "unit"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)


class SwipeSession(Base):
    __tablename__ = "swipe_session"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    status = Column(
        sqlalchemy.Enum(
            SwipeSessionEnum, values_callable=lambda x: [e.value for e in x]
        ),
        default=SwipeSessionEnum.IN_PROGRESS,
    )


class Swipe(Base):
    __tablename__ = "swipe"

    id = Column(Integer, primary_key=True)
    swipe_session_id = Column(Integer, ForeignKey("swipe_session.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    recipe_id = Column(Integer, ForeignKey("recipe.id"))
    like = Column(Boolean, nullable=False)
