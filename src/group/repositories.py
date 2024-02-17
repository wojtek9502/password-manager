import uuid
from typing import List

from sqlalchemy.exc import SQLAlchemyError

from src.common.BaseRepository import BaseRepository, NotFoundEntityError
from src.group.models import GroupModel


class GroupRepository(BaseRepository):
    def model_class(self):
        return GroupModel

    def create(self, name: str) -> GroupModel:
        entity = GroupModel(
            name=name
        )
        return entity

    def update(self, entity_id: uuid.UUID, name: str) -> GroupModel:
        entity: GroupModel = self.get_by_id(entity_id)
        entity.name = name
        return entity

    def find_by_id(self, group_id: uuid.UUID) -> GroupModel:
        try:
            entity = self.query().filter(GroupModel.id == group_id).one()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entity

    def delete_by_id(self, group_id: uuid.UUID) -> uuid.UUID:
        query = self.query().filter(GroupModel.id == group_id)
        entity = query.one_or_none()
        if not entity:
            raise NotFoundEntityError(f"Not found group with uuid: {group_id}")
        entity_uuid = entity.id

        try:
            query.delete()
            self.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

        return entity_uuid
