import hashlib
import os
import secrets
import uuid
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError

from src.common.BaseRepository import BaseRepository, NotFoundEntityError
from src.password.models import PasswordModel


class PasswordRepository(BaseRepository):
    def model_class(self):
        return PasswordModel

    def create_password_hash(self, client_password_encrypted: str,):
        pepper = os.environ['USER_AUTH_PASSWORD_PEPPER']
        if not server_iterations:
            server_iterations = os.environ['USER_AUTH_HASH_N_ITERATIONS']

        if not server_salt:
            server_salt = secrets.token_bytes(int(os.environ['USER_AUTH_SALT_TOKEN_BYTES']))

        hash_value = hashlib.pbkdf2_hmac(
            'sha256',
            client_password_hash.encode('utf-8') + pepper.encode('utf-8'),
            server_salt,
            server_iterations
        )
        return server_salt, hash_value

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
