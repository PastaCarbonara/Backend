from typing import List
from sqlalchemy import select
from app.tag.schemas import CreateTagSchema
from core.db.models import Tag
from core.db import Transactional, session
from core.exceptions.tag import TagAlreadyExistsException


class TagService:
    def __init__(self):
        ...

    async def get_tags(self) -> List[Tag]:
        query = select(Tag)
        result = await session.execute(query)
        return result.scalars().all()

    @Transactional()
    async def create_tag(self, request: CreateTagSchema) -> int:
        tag = await self.get_tag_by_name(request.name)
        if tag:
            raise TagAlreadyExistsException

        db_tag = Tag(**request.dict())

        session.add(db_tag)
        await session.flush()

        return db_tag.id

    async def get_tag_by_id(self, tag_id: int) -> Tag:
        query = select(Tag).where(Tag.id == tag_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_tag_by_name(self, tag_name: str) -> Tag:
        query = select(Tag).where(Tag.name == tag_name)
        result = await session.execute(query)
        return result.scalars().first()
