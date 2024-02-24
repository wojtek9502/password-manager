import datetime
import hashlib
import os
import secrets
import uuid
from typing import Optional, List

from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

from src.common.BaseRepository import BaseRepository, NotFoundEntityError
from src.user.models import UserModel, UserTokenModel, UserGroupModel


class UserRepository(BaseRepository):
    AUTH_SALT_TOKEN_BYTES = int(os.environ['USER_AUTH_SALT_TOKEN_BYTES'])
    AUTH_HASH_N_ITERATIONS = int(os.environ['USER_AUTH_HASH_N_ITERATIONS'])
    AUTH_HASH_ALGO = 'PBKDF2'

    def model_class(self):
        return UserModel

    def create_password_hash(self, password: str, salt: Optional[bytes] = None, iterations: Optional[int] = None):
        pepper = os.environ['USER_AUTH_PASSWORD_PEPPER']
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
        password_crypto_server_side = secrets.token_bytes(4096)  # token to encrypt/decrypt passwords on server side

        entity = UserModel(
            username=username,
            password_hash=password_hash,
            salt=salt,
            hash_algo=hash_algo,
            iterations=iterations,
            password_crypto=password_crypto_server_side
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

    def delete_by_id(self, user_id: uuid.UUID) -> uuid.UUID:
        user_token_repo = UserTokenRepository(session=self.session)
        user_group_repo = UserGroupRepository(session=self.session)
        query = self.query().filter(UserModel.id == user_id)
        entity = query.one_or_none()
        if not entity:
            raise NotFoundEntityError(f"Not found user with uuid: {user_id}")
        entity_uuid = entity.id

        user_token_repo.delete_user_tokens(user_id=user_id)
        user_group_repo.delete_user_from_all_groups(user_id=user_id)

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

    def delete_user_tokens(self, user_id: uuid.UUID):
        entities = self.query().filter(UserTokenModel.user_id == user_id).all()
        try:
            for entity in entities:
                self.session.delete(entity)
            self.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

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


class UserGroupRepository(BaseRepository):
    def model_class(self):
        return UserGroupModel

    def delete_user_from_all_groups(self, user_id: uuid.UUID) -> List[uuid.UUID]:
        query = self.query().filter(UserGroupModel.user_id == user_id)
        entities: List[UserGroupModel] = query.all()
        deleted_password_ids = []

        for user_group_entity in entities:
            try:
                query.delete()
                self.commit()
                deleted_password_ids.append(user_group_entity.user_id)
            except SQLAlchemyError as e:
                self.session.rollback()
                raise e

        return deleted_password_ids
