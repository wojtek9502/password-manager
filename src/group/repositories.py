import uuid
from typing import List

from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

from src import UserModel, PasswordModel
from src.common.BaseRepository import BaseRepository, NotFoundEntityError
from src.group.models import GroupModel
from src.user.repositories import UserRepository


class GroupRepository(BaseRepository):
    def model_class(self):
        return GroupModel

    def create_group(self, name: str) -> GroupModel:
        entity = GroupModel(
            name=name
        )
        return entity

    def create_group_with_user(self, name: str, user_id: uuid.UUID) -> GroupModel:
        entity = GroupModel(
            name=name
        )
        user_entity = UserRepository(session=self.session).get_by_id(user_id)
        entity.users.append(user_entity)
        return entity

    def update(self, entity_id: uuid.UUID, name: str) -> GroupModel:
        entity: GroupModel = self.get_by_id(entity_id)
        entity.name = name
        return entity

    def get_all(self) -> List[GroupModel]:
        try:
            entity = self.query().all()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entity

    def find_groups_by_ids(self, groups_ids: List[uuid.UUID]) -> List[GroupModel]:
        try:
            entity = self.query().filter(GroupModel.id.in_(groups_ids)).all()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entity

    def find_groups_by_user_id(self, user_id: uuid.UUID) -> List[GroupModel]:
        try:
            entity = self.query().join(GroupModel.users).filter(UserModel.id == user_id).all()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entity

    def find_groups_by_password_id(self, password_id: uuid.UUID) -> List[GroupModel]:
        try:
            entity = self.query().join(GroupModel.passwords).filter_by(PasswordModel.id == password_id).all()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entity

    def find_user_default_group(self, user_id: uuid.UUID, ) -> GroupModel:
        try:
            entity = self.query().join(GroupModel.users).filter(
                and_(
                    UserModel.id == user_id,
                    GroupModel.name == 'default'
                )
            ).one()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
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
