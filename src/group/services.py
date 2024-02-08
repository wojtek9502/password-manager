import logging
import uuid
from typing import Optional, List

from src.group.models import GroupModel
from src.group.repositories import GroupRepository

logger = logging.getLogger()


class GroupService:
    @staticmethod
    def create_group() -> GroupModel:
        repo = GroupRepository()
        ...

    @staticmethod
    def update_group() -> Optional[GroupModel]:
        repo = GroupModel()
        ...

    @staticmethod
    def delete_group(user_id: uuid.UUID) -> uuid.UUID:
        repo = GroupModel()
        ...

    @staticmethod
    def find_all_by_user() -> List[GroupModel]:
        repo = GroupModel()
        ...

