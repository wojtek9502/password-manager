import logging
import uuid
from typing import Optional, List

from src.password.models import PasswordModel
from src.password.repositories import PasswordRepository

logger = logging.getLogger()


class PasswordService:
    @staticmethod
    def get(password_id: uuid.UUID) -> PasswordModel:
        repo = PasswordRepository()
        ...

    @staticmethod
    def create(password_from_client_details: str, user_id: uuid.UUID) -> PasswordModel:
        repo = PasswordRepository()
        ...

    @staticmethod
    def update() -> Optional[PasswordModel]:
        repo = PasswordRepository()
        ...

    @staticmethod
    def delete(user_id: uuid.UUID) -> uuid.UUID:
        repo = PasswordRepository()
        ...

    @staticmethod
    def find_all_by_user(user_id: uuid.UUID) -> List[PasswordModel]:
        repo = PasswordRepository()
        ...

    @staticmethod
    def find_all_by_group(group_id: uuid.UUID) -> List[PasswordModel]:
        repo = PasswordRepository()
        ...

