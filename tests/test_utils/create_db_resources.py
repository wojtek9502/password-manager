import uuid
from typing import Tuple, List

from sqlalchemy.orm import Session

from src import GroupModel, PasswordModel
from src.group.services import GroupService
from src.password.cryptography import CryptographyFernet
from src.password.services import PasswordHistoryService, PasswordService
from src.password.types import PasswordDTO, PasswordHistoryDTO
from src.user.services import UserService, UserTokenService


def create_group(session: Session, group_name: str = 'test') -> GroupModel:
    group_service = GroupService(session=session)
    group_entity = group_service.create_group(name=group_name)
    return group_entity


def create_group_with_user(session: Session, user_id: uuid.UUID, group_name: str = 'test') -> GroupModel:
    group_service = GroupService(session=session)
    group_entity = group_service.create_group_with_user(name=group_name, user_id=user_id)
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


def create_client_side_password_encrypted(password_clear: str = 'password') -> bytes:
    client_side_password_encrypted = CryptographyFernet().password_encrypt(
        message=password_clear.encode(),
        additional_pepper='f65ad83a6ec4bfc511d9924520d74bb20d7ca7631efdff0a028ae141bef3d820',
        iterations=600_000
    )
    return client_side_password_encrypted


def create_password(session: Session, user_id: uuid.UUID, group_ids=None,
                    name: str = 'test', login: str = 'test@test.pl', password: str = 'pass') -> PasswordModel:
    if group_ids is None:
        group_ids = []

    password_service = PasswordService(session=session)
    password_dto: PasswordDTO = PasswordDTO(
            name=name,
            login=login,
            server_side_algo='Fernet',
            server_side_iterations=600_000,
            password_encrypted=password.encode(),
            client_side_algo='Fernet',
            client_side_iterations=600_000,
            note='',
            urls=[],
            groups_ids=group_ids,
            user_id=user_id
        )
    password_entity = password_service.create(password_details=password_dto)
    return password_entity
