from core.repository.base import BaseRepo
from core.db.models import (
    Group,
)

class GroupRepository(BaseRepo):
    def __init__(self):
        super().__init__(Group)