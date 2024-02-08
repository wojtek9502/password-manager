import uuid
from typing import List

from sqlalchemy.exc import SQLAlchemyError

from src.common.BaseRepository import BaseRepository, NotFoundEntityError
from src.password.models import PasswordModel


class PasswordRepository(BaseRepository):
    def model_class(self):
        return PasswordModel

    def create(self) -> PasswordModel:
        ...

    def update(self) -> PasswordModel:
        ...

    def find_all_by_user(self, user_id: uuid.UUID) -> List[PasswordModel]:
        ...

    def find_by_id(self, group_id: uuid.UUID) -> PasswordModel:
        try:
            entity = self.query().filter(PasswordModel.id == group_id).one()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entity

    def delete(self, password_id: uuid.UUID, user_id: uuid.UUID) -> uuid.UUID:
        query = self.query()\
            .filter(PasswordModel.id == password_id)\
            .filter(PasswordModel.user_id == user_id)
        entity = query.one_or_none()
        if not entity:
            raise NotFoundEntityError(f"Not found password with uuid: {password_id} for user {user_id}")
        entity_uuid = entity.id

        try:
            query.delete()
            self.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

        return entity_uuid
