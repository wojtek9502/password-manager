from src import GroupModel
from src.group.services import GroupService
from src.password.cryptography import CryptographyFernet
from src.user.services import UserService


def mock_client_side_password_encrypted() -> bytes:
    client_side_password_encrypted = CryptographyFernet().password_encrypt(
        message='password'.encode(),
        additional_pepper='f65ad83a6ec4bfc511d9924520d74bb20d7ca7631efdff0a028ae141bef3d820',
        iterations=600_000
    )
    return client_side_password_encrypted


def mock_password_group(group_name: str) -> GroupModel:
    service = GroupService()
    entity = service.create(
        name=group_name
    )

    return entity


def mock_user(username: str, password_clear: str) -> GroupModel:
    service = UserService()
    entity = service.create_user(
        username=username,
        password_clear=password_clear
    )
    return entity