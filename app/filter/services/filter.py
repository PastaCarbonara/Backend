from app.filter.repository.filter import FilterRepository
from app.tag.repository.tag import TagRepository
from app.user.repository.user import UserRepository
from app.user.exception.user import UserNotFoundException
from core.db import Transactional
from core.db.models import Tag, Recipe


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

        filters = await self.filter_repository.get_all_filters_user(user_id)
        tags = await self.tag_repository.get_tags()

        new_filters = [
            filter
            for filter in user_filters
            if filter not in [filter.id for filter in filters]
            and filter in [tag.id for tag in tags]
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

    async def get_filtered_recipes_user(self, user_id) -> list[Recipe]:
        """Get all recipes for a user."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return await self.filter_repository.get_filtered_recipes_user(user_id)

    async def get_filtered_recipes_group(self, group_id) -> list[Recipe]:
        """Get all recipes for a group."""
        return await self.filter_repository.get_filtered_recipes_group(group_id)
