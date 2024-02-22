import uuid

from src import UserModel, PasswordModel
from src.password.cryptography import CryptographyFernet
from src.password.types import PasswordHistoryDTO, PasswordDTO
from src.user.repositories import UserRepository


def _encrypt_password_server_side(session, password_client_side_encrypted: bytes,
                                  iterations: int, user_id: uuid.UUID) -> bytes:
    user_repo = UserRepository(session=session)
    user_entity: UserModel = user_repo.get_by_id(user_id)
    if not user_entity:
        raise Exception(f"No user with id = {user_id}")

    fernet_crypto = CryptographyFernet()
    password_encrypted_by_server = fernet_crypto.password_encrypt(
        message=password_client_side_encrypted,
        additional_pepper=str(user_entity.password_crypto),
        iterations=iterations
    )
    return password_encrypted_by_server


def _decrypt_password_server_side(session, password_server_side_encrypted: bytes, user_id: uuid.UUID) -> bytes:
    user_repo = UserRepository(session=session)
    user_entity: UserModel = user_repo.get_by_id(user_id)
    if not user_entity:
        raise Exception(f"No user with id = {user_id}")

    fernet_crypto = CryptographyFernet()
    password_decrypted_by_server = fernet_crypto.password_decrypt(
        token=password_server_side_encrypted,
        password_to_decrypt=str(user_entity.password_crypto)
    )

    return password_decrypted_by_server


def create_password_dto(password_entity: PasswordModel, password_client_side_encrypted: bytes):
    password_urls = [url.url for url in password_entity.urls]
    password_groups_dtos = []
    password_history_dtos = []
    for password_history in password_entity.history:
        history_dto = PasswordHistoryDTO(
            id=password_history.id,
            name=password_history.name,
            login=password_history.login,
            client_side_password_encrypted=password_history.client_side_password_encrypted,
            client_side_algo=password_history.client_side_algo,
            client_side_iterations=password_history.client_side_iterations,
            note=password_history.note,
            password_id=password_history.password_id,
            user_id=password_history.user_id,
        )
        password_history_dtos.append(history_dto)

    password_dto = PasswordDTO(
        id=password_entity.id,
        name=password_entity.name,
        login=password_entity.login,
        password_encrypted=password_client_side_encrypted,
        client_side_algo=password_entity.client_side_algo,
        client_side_iterations=password_entity.server_side_iterations,
        server_side_algo=password_entity.server_side_algo,
        server_side_iterations=password_entity.server_side_iterations,
        note=password_entity.note,
        user_id=password_entity.user_id,
        history=password_history_dtos,
        groups_ids=password_groups_dtos,
        urls=password_urls
    )
    return password_dto
