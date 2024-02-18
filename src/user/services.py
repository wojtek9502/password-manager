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

from src.common.BaseService import BaseService
from src.user.models import UserModel
from src.common.BaseRepository import NotFoundEntityError
from src.user.exceptions import UserLoginPasswordInvalidError, MasterTokenInvalidUseError
from src.user.models import UserTokenModel
from src.user.repositories import UserRepository, UserTokenRepository
from src.user.types import UserJwtTokenPayload

logger = logging.getLogger()


class UserJwtTokenService(BaseService):
    def create(self, username: str) -> Optional[str]:
        if not username:
            return None

        payload = dataclasses.asdict(UserJwtTokenPayload(username=username))
        user_password_hash = UserRepository(self.session).find_by_username(username).password_hash
        key = os.environ['JTW_TOKEN_PEPPER'] + "-" + str(base64.b64encode(user_password_hash))
        encoded_jwt = jwt.encode(payload=payload, key=key, algorithm="HS256")
        return encoded_jwt

    def is_valid(self, jwt_token: str, username: str) -> bool:
        if not username:
            return False

        valid_payload = dataclasses.asdict(UserJwtTokenPayload(username=username))
        user_password_hash = UserRepository(self.session).find_by_username(username).password_hash
        key = os.environ['JTW_TOKEN_PEPPER'] + "-" + str(base64.b64encode(user_password_hash))

        try:
            payload = jwt.decode(jwt=jwt_token, key=key, algorithms=["HS256"])
        except DecodeError:
            return False

        if payload == valid_payload:
            return True
        return False

    def decode(self, jwt_token: str, username: str) -> Optional[UserJwtTokenPayload]:
        if not username:
            return None

        valid_payload = dataclasses.asdict(UserJwtTokenPayload(username=username))
        user_password_hash = UserRepository(self.session).find_by_username(username).password_hash
        key = os.environ['JTW_TOKEN_PEPPER'] + "-" + str(base64.b64encode(user_password_hash))
        decoded_payload = jwt.decode(jwt=jwt_token, key=key, algorithms=["HS256"])

        if decoded_payload != valid_payload:
            return None

        token_decode = UserJwtTokenPayload(
            username=decoded_payload['username']
        )
        return token_decode


class UserService(BaseService):
    def login_user(self, username: str, password_clear: str) -> str:
        repo = UserRepository(session=self.session)
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

        user_logged_jwt_token = UserJwtTokenService(session=self.session).create(username=username)
        return user_logged_jwt_token


    def create_user(self, username: str, password_clear: str) -> UserModel:
        repo = UserRepository(session=self.session)
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

    def update_user(self, user_id: uuid.UUID, password_clear: str) -> Optional[UserModel]:
        repo = UserRepository(session=self.session)

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

    def delete_user(self, user_id: uuid.UUID) -> uuid.UUID:
        repo = UserRepository(session=self.session)
        try:
            entity_uuid = repo.delete_by_uuid(
                user_uuid=user_id,
            )
        except NotFoundEntityError as e:
            repo.session.rollback()
            raise e

        return entity_uuid

    def find_all(self) -> List[UserModel]:
        repo = UserRepository(session=self.session)
        entities = repo.find_all()
        return entities

    def find_by_username(self, username: str) -> Optional[UserModel]:
        repo = UserRepository(session=self.session)
        try:
            entity = repo.find_by_username(username=username)
        except (SQLAlchemyError, NotFoundEntityError) as e:
            repo.session.close()
            raise e
        return entity

    def find_id_by_token(self, token: str) -> Optional[uuid.UUID]:
        if token == os.environ['API_AUTH_MASTER_TOKEN']:
            raise MasterTokenInvalidUseError('Master token cannot be use here')

        repo = UserTokenRepository(session=self.session)
        try:
            entity = repo.find_by_token(token=token)
        except (SQLAlchemyError, NotFoundEntityError) as e:
            repo.session.close()
            raise e
        return entity.user_id


class UserTokenService(BaseService):

    def create_token(self, token, user_id: uuid.UUID, expiration_date: Optional[datetime.datetime] = None) -> UserTokenModel:
        repo = UserTokenRepository(session=self.session)

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
        repo = UserTokenRepository(session=self.session)
        repo.delete_expired_tokens()
        token_entity = repo.find_by_token(token=token)

        if not token_entity:
            return False
        return True

    def delete_expired_tokens(self):
        repo = UserTokenRepository(session=self.session)
        repo.delete_expired_tokens()

    def get_all(self) -> List[UserTokenModel]:
        repo = UserTokenRepository(session=self.session)
        entities = repo.find_all()
        return entities
