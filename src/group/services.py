import logging
import uuid
from typing import Optional, List

from src.group.models import GroupModel
from src.group.repositories import GroupRepository

logger = logging.getLogger()


class GroupService:
    @staticmethod
    def create(name: str) -> GroupModel:
        repo = GroupRepository()
        entity = repo.create(name=name)
        repo.save(entity)
        repo.commit()
        return entity

    @staticmethod
    def update(group_id: uuid.UUID, new_name: str) -> Optional[GroupModel]:
        repo = GroupRepository()
        entity = repo.update(
            entity_id=group_id,
            name=new_name
        )
        repo.save(entity)
        repo.commit()
        return entity

    @staticmethod
    def delete(group_id: uuid.UUID) -> uuid.UUID:
        repo = GroupRepository()
        repo.find_by_id(group_id=group_id)
        return group_id

