"""Database models."""

from datetime import datetime
from typing import List
import uuid
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    JSON,
    func,
)

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from core.db import Base
from core.db.mixins import TimestampMixin
from core.db.enums import SwipeSessionEnum, TagType
from core.config import config


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
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    client_token: Mapped[uuid.UUID] = mapped_column(unique=True, nullable=False)

    account_auth: Mapped["AccountAuth"] = relationship(back_populates="user")
    recipes: Mapped[List["Recipe"]] = relationship(back_populates="creator")
    judged_recipes: Mapped[List[RecipeJudgement]] = relationship(back_populates="user")
    groups: Mapped[List["GroupMember"]] = relationship(back_populates="user")
    filters: Mapped[List["UserTag"]] = relationship(back_populates="user")


class AccountAuth(Base, TimestampMixin):
    __tablename__ = "account_auth"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column()

    user: Mapped[User] = relationship(back_populates="account_auth")


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

class UserTag(Base):
    __tablename__ = "user_tag"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True)

    user: Mapped["User"] = relationship(back_populates="filters")
    tag: Mapped["Tag"] = relationship(back_populates="users")

class File(Base):
    __tablename__ = "file"

    filename: Mapped[str] = mapped_column(String(), primary_key=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="image")
    group: Mapped["Group"] = relationship(back_populates="image")

    @hybrid_property
    def file_url(self):
        return config.AZURE_IMAGE_URL_BASE + self.filename


class Recipe(Base, TimestampMixin):
    __tablename__ = "recipe"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column()
    instructions = Column(JSON, nullable=False)
    materials = Column(JSON, nullable=True)
    preparation_time: Mapped[int | None] = mapped_column()
    filename: Mapped[str] = mapped_column(
        ForeignKey("file.filename", ondelete="CASCADE")
    )
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    image: Mapped[File] = relationship(back_populates="recipe")
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
            + f"preparation_time='{self.preparation_time}' "
            + f"image='{self.image}' "
            + f"creator_id='{self.creator_id}' "
        )
    
    @hybrid_property
    def likes(self):
        return len([judgement for judgement in self.judgements if judgement.like])


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    tag_type: Mapped[TagType] = mapped_column()

    recipes: Mapped[RecipeTag] = relationship(back_populates="tag")
    users: Mapped[UserTag] = relationship(back_populates="tag")


class Ingredient(Base):
    __tablename__ = "ingredient"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    recipes: Mapped[RecipeIngredient] = relationship(back_populates="ingredient")


class SwipeSession(Base, TimestampMixin):
    __tablename__ = "swipe_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_date: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now()
    )
    status: Mapped[SwipeSessionEnum] = mapped_column(default=SwipeSessionEnum.READY)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), nullable=True)

    swipes: Mapped[List["Swipe"]] = relationship(
        back_populates="swipe_session", uselist=True
    )
    group: Mapped["Group"] = relationship(back_populates="swipe_sessions")

    def __repr__(self) -> str:
        return f"SwipeSession({self.id}, {self.session_date}, {self.status})"


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
    filename: Mapped[str] = mapped_column(
        ForeignKey("file.filename", ondelete="CASCADE")
    )

    image: Mapped[File] = relationship(back_populates="group")
    users: Mapped[List["GroupMember"]] = relationship(back_populates="group")
    swipe_sessions: Mapped[List[SwipeSession]] = relationship(back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_member"

    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    is_admin: Mapped[bool] = mapped_column(default=False)

    group: Mapped[Group] = relationship(back_populates="users")
    user: Mapped[User] = relationship(back_populates="groups")
