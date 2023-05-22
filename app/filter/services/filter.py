from app.filter.repository.filter import FilterRepository
from app.tag.repository.tag import TagRepository
from app.user.repository.user import UserRepository
from app.user.exceptions.user import UserNotFoundException
from core.db import Transactional
from core.db.models import Tag


class FilterService:
    def __init__(self):
        self.filter_repository: FilterRepository = FilterRepository()
        self.tag_repository: TagRepository = TagRepository()
        self.user_repository: UserRepository = UserRepository()

    @Transactional()
    async def store_filter(self, user_id: int, user_filter: int):
        """Store a filter for a user."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        await self.filter_repository.store_filter(user_id, user_filter)

    @Transactional()
    async def store_filters(self, user_id, user_filters: list[int]):
        """Store filters for a user."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()

        stored_filters = await self.filter_repository.get_all_filters_user(user_id)
        stored_filters_ids = [stored_filter.id for stored_filter in stored_filters]
        tags = await self.tag_repository.get_tags()
        stored_tags_ids = [tag.id for tag in tags]

        new_filters = [
            filter_id
            for filter_id in user_filters
            if filter_id not in stored_filters_ids and filter_id in stored_tags_ids
        ]

        await self.filter_repository.store_filters(user_id, new_filters)

    @Transactional()
    async def delete_filter(self, user_id, tag_id):
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        await self.filter_repository.delete_filter_user(user_id, tag_id)

    async def get_all_filters_user(self, user_id) -> list[Tag]:
        """Get all filters for a user."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return await self.filter_repository.get_all_filters_user(user_id)
