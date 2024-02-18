import uuid

from sqlalchemy.orm import Session

from src import GroupModel
from src.group.services import GroupService
from src.password.cryptography import CryptographyFernet
from src.password.services import PasswordHistoryService
from src.password.types import PasswordHistoryDTO, PasswordDTO
from src.user.services import UserService


def mock_client_side_password_encrypted(password_clear: str = 'password') -> bytes:
    client_side_password_encrypted = CryptographyFernet().password_encrypt(
        message=password_clear.encode(),
        additional_pepper='f65ad83a6ec4bfc511d9924520d74bb20d7ca7631efdff0a028ae141bef3d820',
        iterations=600_000
    )
    return client_side_password_encrypted


def mock_password_group(db_session: Session, group_name: str) -> GroupModel:
    service = GroupService(session=db_session)
    entity = service.create(
        name=group_name
    )

    return entity

def mock_password_history(db_session: Session, password_id: uuid.UUID, password_details: PasswordDTO) -> GroupModel:
    service = PasswordHistoryService(session=db_session)
    entity = service.create(
        password_history_details=PasswordHistoryDTO(
                name=password_details.name,
                login=password_details.login,
                client_side_password_encrypted=password_details.client_side_password_encrypted,
                server_side_algo=password_details.server_side_algo,
                server_side_iterations=password_details.server_side_iterations,
                client_side_algo=password_details.client_side_algo,
                client_side_iterations=password_details.client_side_iterations,
                note=password_details.note,
                user_id=password_details.user_id,
                password_id=password_id
            )
    )

    return entity

def mock_user(db_session: Session, username: str, password_clear: str) -> GroupModel:
    service = UserService(session=db_session)
    entity = service.create_user(
        username=username,
        password_clear=password_clear
    )
    return entity
