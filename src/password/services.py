import logging
import uuid
from typing import Optional, List

from src.group.repositories import GroupRepository
from src.password.models import PasswordModel

logger = logging.getLogger()


class GroupService:
    @staticmethod
    def create_group() -> PasswordModel:
        repo = GroupRepository()
        ...

    @staticmethod
    def update_group() -> Optional[PasswordModel]:
        repo = PasswordModel()
        ...

    @staticmethod
    def delete_group(user_id: uuid.UUID) -> uuid.UUID:
        repo = PasswordModel()
        ...

    @staticmethod
    def find_all_by_user() -> List[PasswordModel]:
        repo = PasswordModel()
        ...

