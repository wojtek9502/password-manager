import base64
import dataclasses
import datetime
import logging
import os
import uuid
from typing import Optional, List

import jwt
import sqlalchemy
from jwt import DecodeError
from sqlalchemy.exc import SQLAlchemyError

from src.user.models import UserModel
from src.common.BaseRepository import NotFoundEntityError
from src.user.exceptions import UserLoginPasswordInvalidError, MasterTokenInvalidUseError
from src.user.models import UserTokenModel
from src.user.repositories import UserRepository, UserTokenRepository
from src.user.types import UserJwtTokenPayload

logger = logging.getLogger()


class UserJwtTokenService:
    @staticmethod
    def create(username: str) -> Optional[str]:
        if not username:
            return None

        payload = dataclasses.asdict(UserJwtTokenPayload(username=username))
        user_password_hash = UserRepository().find_by_username(username).password_hash
        key = os.environ['JTW_TOKEN_PEPPER'] + "-" + str(base64.b64encode(user_password_hash))
        encoded_jwt = jwt.encode(payload=payload, key=key, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def is_valid(jwt_token: str, username: str) -> bool:
        if not username:
            return False

        valid_payload = dataclasses.asdict(UserJwtTokenPayload(username=username))
        user_password_hash = UserRepository().find_by_username(username).password_hash
        key = os.environ['JTW_TOKEN_PEPPER'] + "-" + str(base64.b64encode(user_password_hash))

        try:
            payload = jwt.decode(jwt=jwt_token, key=key, algorithms=["HS256"])
        except DecodeError:
            return False

        if payload == valid_payload:
            return True
        return False

    @staticmethod
    def decode(jwt_token: str, username: str) -> Optional[UserJwtTokenPayload]:
        if not username:
            return None

        valid_payload = dataclasses.asdict(UserJwtTokenPayload(username=username))
        user_password_hash = UserRepository().find_by_username(username).password_hash
        key = os.environ['JTW_TOKEN_PEPPER'] + "-" + str(base64.b64encode(user_password_hash))
        decoded_payload = jwt.decode(jwt=jwt_token, key=key, algorithms=["HS256"])

        if decoded_payload != valid_payload:
            return None

        token_decode = UserJwtTokenPayload(
            username=decoded_payload['username']
        )
        return token_decode


class UserService:
    @staticmethod
    def login_user(username: str, password_clear: str) -> str:
        repo = UserRepository()
        try:
            entity = repo.find_by_username(username=username)
        except (SQLAlchemyError, NotFoundEntityError):
            repo.session.close()
            raise UserLoginPasswordInvalidError(f"Invalid username or password")

        # recreate user hash with salt and iterations from user entity
        password_salt_from_user_input, password_hash_from_user_input = repo.create_password_hash(
            password=password_clear,
            salt=entity.salt,
            iterations=entity.iterations
        )
        password_hash_from_db = entity.password_hash
        if not password_hash_from_db == password_hash_from_user_input:
            repo.session.close()
            raise UserLoginPasswordInvalidError()

        user_logged_jwt_token = UserJwtTokenService.create(username=username)
        return user_logged_jwt_token

    @staticmethod
    def create_user(username: str, password_clear: str) -> UserModel:
        repo = UserRepository()
        entity = repo.create(
            username=username,
            password_clear=password_clear,
        )
        try:
            repo.save(entity)
            repo.commit()
        except SQLAlchemyError as e:
            repo.session.rollback()
            raise e

        return entity

    @staticmethod
    def update_user(user_id: uuid.UUID, password_clear: str) -> Optional[UserModel]:
        repo = UserRepository()

        try:
            entity = repo.find_by_id(user_id)
        except sqlalchemy.exc.NoResultFound as e:
            logger.error(str(e))
            raise NotFoundEntityError(f"Not found user with user_id {user_id}")

        entity = repo.update(
            entity=entity,
            username=entity.username,
            password_clear=password_clear
        )
        return entity

    @staticmethod
    def delete_user(user_id: uuid.UUID) -> uuid.UUID:
        repo = UserRepository()
        try:
            entity_uuid = repo.delete_by_uuid(
                user_uuid=user_id,
            )
        except NotFoundEntityError as e:
            repo.session.rollback()
            raise e

        return entity_uuid

    @staticmethod
    def find_all() -> List[UserModel]:
        repo = UserRepository()
        entities = repo.find_all()
        return entities

    @staticmethod
    def find_by_username(username: str) -> Optional[UserModel]:
        repo = UserRepository()
        try:
            entity = repo.find_by_username(username=username)
        except (SQLAlchemyError, NotFoundEntityError) as e:
            repo.session.close()
            raise e
        return entity

    @staticmethod
    def find_id_by_token(token: str) -> Optional[uuid.UUID]:
        if token == os.environ['API_AUTH_MASTER_TOKEN']:
            raise MasterTokenInvalidUseError('Master token cannot be use here')

        repo = UserTokenRepository()
        try:
            entity = repo.find_by_token(token=token)
        except (SQLAlchemyError, NotFoundEntityError) as e:
            repo.session.close()
            raise e
        return entity.user_id


class UserTokenService:
    def create_token(self, token, user_id: uuid.UUID, expiration_date: Optional[datetime.datetime] = None) -> UserTokenModel:
        repo = UserTokenRepository()

        repo.delete_expired_tokens()
        old_token_entity = repo.find_by_token(token=token)

        if not old_token_entity:
            new_entity = repo.create(
                token=token,
                user_id=user_id,
                expiration_date=expiration_date
            )
            repo.save(new_entity)
            repo.commit()
            return new_entity
        return old_token_entity

    def is_token_valid(self, token: str) -> bool:
        """
        Token has expired date, first delete expired token. If token still exists in db then is valid
        :param token:
        :return bool:
        """
        repo = UserTokenRepository()
        repo.delete_expired_tokens()
        token_entity = repo.find_by_token(token=token)

        if not token_entity:
            return False
        return True

    def delete_expired_tokens(self):
        repo = UserTokenRepository()
        repo.delete_expired_tokens()

    def get_all(self) -> List[UserTokenModel]:
        repo = UserTokenRepository()
        entities = repo.find_all()
        return entities
