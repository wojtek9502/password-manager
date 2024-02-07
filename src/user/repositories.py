import datetime
import hashlib
import os
import secrets
import uuid
from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError

from src.common.BaseRepository import BaseRepository, NotFoundEntityError
from src.user.models import UserModel, UserTokenModel


class UserRepository(BaseRepository):
    AUTH_SALT_TOKEN_BYTES = 128
    AUTH_HASH_N_ITERATIONS = 100000
    AUTH_HASH_ALGO = 'PBKDF2'

    def model_class(self):
        return UserModel

    def create_password_hash(self, password: str, salt: Optional[bytes] = None, iterations: Optional[int] = None):
        pepper = os.environ['USER_AUTH_PEPPER']
        if not iterations:
            iterations = self.AUTH_HASH_N_ITERATIONS

        if not salt:
            salt = secrets.token_bytes(self.AUTH_SALT_TOKEN_BYTES)

        hash_value = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8') + pepper.encode('utf-8'),
            salt,
            iterations
        )
        return salt, hash_value

    def create(self, username: str, password_clear: str) -> UserModel:
        salt, password_hash = self.create_password_hash(password=password_clear)
        hash_algo = self.AUTH_HASH_ALGO
        iterations = self.AUTH_HASH_N_ITERATIONS

        entity = UserModel(
            username=username,
            password_hash=password_hash,
            salt=salt,
            hash_algo=hash_algo,
            iterations=iterations
        )
        return entity

    def update(self, entity: UserModel, username: str, password_clear: str) -> UserModel:
        salt, password_hash = self.create_password_hash(password=password_clear)
        hash_algo = self.AUTH_HASH_ALGO
        iterations = self.AUTH_HASH_N_ITERATIONS

        entity.username = username
        entity.password_hash = password_hash
        entity.salt = salt
        entity.hash_algo = hash_algo
        entity.iterations = iterations

        try:
            self.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entity

    def find_all(self) -> List[UserModel]:
        return self.query().all()

    def find_by_username(self, username: str) -> UserModel:
        try:
            entity = self.query().filter(UserModel.username == username).one()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entity

    def find_by_id(self, user_id: uuid.UUID) -> UserModel:
        try:
            entity = self.query().filter(UserModel.id == user_id).one()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entity

    def delete_by_uuid(self, user_uuid: uuid.UUID) -> uuid.UUID:
        query = self.query().filter(UserModel.id == user_uuid)
        entity = query.one_or_none()
        if not entity:
            raise NotFoundEntityError(f"Not found user with uuid: {user_uuid}")
        entity_uuid = entity.id

        try:
            query.delete()
            self.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

        return entity_uuid


class UserTokenRepository(BaseRepository):
    def model_class(self):
        return UserTokenModel

    def create(self, token: str, user_id: uuid.UUID, expiration_date: Optional[datetime.datetime] = None) -> UserModel:
        if not expiration_date:
            token_expiration_date_hours = int(os.environ['JWT_TOKEN_EXPIRATION_DATE_HOURS'])
            expiration_date = datetime.datetime.now() + datetime.timedelta(hours=token_expiration_date_hours)

        entity = UserTokenModel(
            token=token,
            expiration_date=expiration_date,
            user_id=user_id
        )
        return entity

    def delete_expired_tokens(self):
        date_now = datetime.datetime.now()
        entities = self.query().filter(UserTokenModel.expiration_date < date_now).all()
        try:
            for entity in entities:
                self.session.delete(entity)
            self.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def find_by_token(self, token: str) -> Optional[UserTokenModel]:
        entity = self.query().filter(UserTokenModel.token == token).one_or_none()
        if entity:
            return entity
        return None

    def find_all(self) -> List[UserTokenModel]:
        entities = self.query().all()
        return entities