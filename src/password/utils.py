import uuid

from src import UserModel
from src.password.cryptography import CryptographyFernet
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
