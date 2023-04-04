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

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipe.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    like: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="judged_recipes")
    recipe: Mapped["Recipe"] = relationship(back_populates="judgements")


class User(Base, TimestampMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)

    profile: Mapped["UserProfile"] = relationship(back_populates="user", lazy="joined")
    recipes: Mapped[List["Recipe"]] = relationship(back_populates="creator")
    judged_recipes: Mapped[List[RecipeJudgement]] = relationship(back_populates="user")
    groups: Mapped[List["GroupMember"]] = relationship(back_populates="user")


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profile"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column()
    is_admin: Mapped[bool] = mapped_column(default=False)

    user: Mapped[User] = relationship(back_populates="profile")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredient"

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipe.id", ondelete="CASCADE"), primary_key=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredient.id"), primary_key=True
    )
    unit: Mapped[str] = mapped_column()
    amount: Mapped[float] = mapped_column()

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipes")


class RecipeTag(Base):
    __tablename__ = "recipe_tag"

    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipe.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    )

    recipe: Mapped["Recipe"] = relationship(back_populates="tags")
    tag: Mapped["Tag"] = relationship(back_populates="recipes")


class File(Base):
    __tablename__ = "file"

    filename: Mapped[str] = mapped_column(String(), primary_key=True)


class Recipe(Base, TimestampMixin):
    __tablename__ = "recipe"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column()
    instructions = Column(JSON, nullable=False)
    preparing_time: Mapped[int | None] = mapped_column()
    image: Mapped[str] = mapped_column(ForeignKey("file.filename", ondelete="CASCADE"))
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))

    # ingredients = Column(JSON, nullable=False)
    ingredients: Mapped[List[RecipeIngredient]] = relationship(back_populates="recipe")
    tags: Mapped[List[RecipeTag]] = relationship(back_populates="recipe")
    creator: Mapped[User] = relationship(back_populates="recipes")
    judgements: Mapped[RecipeJudgement] = relationship(back_populates="recipe")

    def __repr__(self) -> str:
        return (
            f"id='{self.id}' "
            + f"name='{self.name}' "
            + f"description='{self.description}' "
            + f"instructions='{self.instructions}' "
            + f"preparing_time='{self.preparing_time}' "
            + f"image='{self.image}' "
            + f"creator_id='{self.creator_id}' "
        )


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    recipes: Mapped[RecipeTag] = relationship(back_populates="tag")


class Ingredient(Base):
    __tablename__ = "ingredient"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    recipes: Mapped[RecipeIngredient] = relationship(back_populates="ingredient")


class SwipeSession(Base, TimestampMixin):
    __tablename__ = "swipe_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[SwipeSessionEnum] = mapped_column(
        default=SwipeSessionEnum.IN_PROGRESS
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), nullable=True)

    swipes: Mapped[List["Swipe"]] = relationship(
        back_populates="swipe_session", uselist=True
    )


class Swipe(Base):
    __tablename__ = "swipe"

    id: Mapped[int] = mapped_column(primary_key=True)
    like: Mapped[bool] = mapped_column()
    swipe_session_id: Mapped[int] = mapped_column(ForeignKey("swipe_session.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"))

    swipe_session: Mapped[SwipeSession] = relationship(back_populates="swipes")


class Group(Base, TimestampMixin):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())

    users: Mapped[List["GroupMember"]] = relationship(back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_member"

    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    is_admin: Mapped[bool] = mapped_column(default=False)

    group: Mapped[Group] = relationship(back_populates="users")
    user: Mapped[User] = relationship(back_populates="groups")
