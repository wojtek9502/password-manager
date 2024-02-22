import uuid
from typing import Tuple

from sqlalchemy.orm import Session

from src import GroupModel
from src.group.services import GroupService
from src.password.cryptography import CryptographyFernet
from src.password.services import PasswordHistoryService
from src.password.types import PasswordDTO, PasswordHistoryDTO
from src.user.services import UserService, UserTokenService


def create_group(session: Session, user_id: uuid.UUID, group_name: str = 'test') -> GroupModel:
    group_service = GroupService(session=session)
    group_entity = group_service.create(name=group_name, user_id=user_id)
    return group_entity


def create_test_user_and_get_token(session: Session, user: str = 'test',
                                   password_clear: str = 'test') -> Tuple[uuid.UUID, str]:
    user_service = UserService(session=session)
    user_token_service = UserTokenService(session=session)

    user_entity = user_service.create_user(username=user, password_clear=password_clear)
    user_login_token = user_service.login_user(username=user, password_clear=password_clear)

    user_token_service.create_token(
        token=user_login_token,
        user_id=user_entity.id
    )
    return user_entity.id, user_login_token


def create_user(db_session: Session, username: str, password_clear: str) -> GroupModel:
    service = UserService(session=db_session)
    entity = service.create_user(
        username=username,
        password_clear=password_clear
    )
    return entity


def create_password_history(db_session: Session, password_id: uuid.UUID, password_details: PasswordDTO) -> GroupModel:
    service = PasswordHistoryService(session=db_session)
    entity = service.create(
        password_history_details=PasswordHistoryDTO(
                name=password_details.name,
                login=password_details.login,
                client_side_password_encrypted=password_details.password_encrypted,
                client_side_algo=password_details.client_side_algo,
                client_side_iterations=password_details.client_side_iterations,
                note=password_details.note,
                user_id=password_details.user_id,
                password_id=password_id
            )
    )

    return entity


def create_password_group(db_session: Session, group_name: str) -> GroupModel:
    service = GroupService(session=db_session)
    entity = service.create(
        name=group_name
    )

    return entity


def create_client_side_password_encrypted(password_clear: str = 'password') -> bytes:
    client_side_password_encrypted = CryptographyFernet().password_encrypt(
        message=password_clear.encode(),
        additional_pepper='f65ad83a6ec4bfc511d9924520d74bb20d7ca7631efdff0a028ae141bef3d820',
        iterations=600_000
    )
    return client_side_password_encrypted
