from typing import List
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    JSON,
)

from sqlalchemy.orm import relationship, Mapped, mapped_column

from core.db import Base
from core.db.mixins import TimestampMixin
from core.db.enums import SwipeSessionEnum


class RecipeJudgement(Base, TimestampMixin):
    __tablename__ = "recipe_judgement"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    like: Mapped[bool] = mapped_column(default=False)


class User(Base, TimestampMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)

    profile: Mapped["UserProfile"] = relationship(back_populates="user")
    recipes: Mapped[List["Recipe"]] = relationship(back_populates="creator")
    judged_recipes: Mapped[List["Recipe"]] = relationship(back_populates="users")

    def __repr__(self):
        return f"{self.username} {self.id}"


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profile"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column()
    is_admin: Mapped[bool] = mapped_column(default=False)


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredient"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("receipe.id"), primary_key=True
    )

    amount: Mapped[float] = mapped_column()
    unit_id: Mapped[float] = mapped_column(ForeignKey("unit.id"))


class RecipeTag(Base):
    __tablename__ = "recipe_tag"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id"), primary_key=True)


class Recipe(Base, TimestampMixin):
    __tablename__ = "recipe"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column()
    instructions = Column(JSON, nullable=False)
    preparing_time: Mapped[int | None] = mapped_column()
    image: Mapped[str] = mapped_column()
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))

    ingredients: Mapped[List["Ingredient"]] = relationship(back_populates="recipes")
    tags: Mapped[List["Tag"]] = relationship(back_populates="recipes")
    creator: Mapped[User] = relationship(back_populates="recipes")
    users: Mapped[List[User]] = relationship(back_populates="judged_recipes")

    def __repr__(self) -> str:
        return self.name


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    recipes: Mapped[Recipe] = relationship(back_populates="tags")


class Ingredient(Base):
    __tablename__ = "ingredient"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    recipes: Mapped[Recipe] = relationship(back_populates="ingredients")


class Unit(Base):
    __tablename__ = "unit"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))


class SwipeSession(Base):
    __tablename__ = "swipe_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[SwipeSessionEnum] = mapped_column(
        default=SwipeSessionEnum.IN_PROGRESS
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    swipes: Mapped[List["Swipe"]] = relationship(back_populates="swipe_session")


class Swipe(Base):
    __tablename__ = "swipe"

    id: int = mapped_column(primary_key=True)

    like: Mapped[bool] = mapped_column()
    swipe_session_id: Mapped[int] = mapped_column(ForeignKey("swipe_session.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"))

    swipe_session: Mapped[SwipeSession] = relationship(back_populates="swipes")
