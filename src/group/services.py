import logging
import uuid
from typing import Optional

from src.common.BaseService import BaseService
from src.group.models import GroupModel
from src.group.repositories import GroupRepository

logger = logging.getLogger()


class GroupService(BaseService):
    def create(self, name: str) -> GroupModel:
        repo = GroupRepository(session=self.session)
        entity = repo.create(name=name)
        repo.save(entity)
        repo.commit()
        return entity

    def update(self, group_id: uuid.UUID, new_name: str) -> Optional[GroupModel]:
        repo = GroupRepository(session=self.session)
        entity = repo.update(
            entity_id=group_id,
            name=new_name
        )
        repo.save(entity)
        repo.commit()
        return entity

    def delete(self, group_id: uuid.UUID) -> uuid.UUID:
        repo = GroupRepository(session=self.session)
        repo.find_by_id(group_id=group_id)
        return group_id

