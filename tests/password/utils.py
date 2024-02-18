from sqlalchemy.orm import Session

from src import GroupModel
from src.group.services import GroupService
from src.password.cryptography import CryptographyFernet
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


def mock_user(db_session: Session, username: str, password_clear: str) -> GroupModel:
    service = UserService(session=db_session)
    entity = service.create_user(
        username=username,
        password_clear=password_clear
    )
    return entity
