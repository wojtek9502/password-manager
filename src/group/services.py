import logging
import uuid
from typing import Optional, List

from src.group.models import GroupModel
from src.group.repositories import GroupRepository

logger = logging.getLogger()


class GroupService:
    @staticmethod
    def create() -> GroupModel:
        repo = GroupRepository()
        ...

    @staticmethod
    def update() -> Optional[GroupModel]:
        repo = GroupModel()
        ...

    @staticmethod
    def delete(user_id: uuid.UUID) -> uuid.UUID:
        repo = GroupModel()
        ...

    @staticmethod
    def find_all_by_user() -> List[GroupModel]:
        repo = GroupModel()
        ...

