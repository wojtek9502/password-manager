import logging
import uuid
from typing import List

from src import UserModel
from src.password.cryptography import CryptographyFernet
from src.password.models import PasswordModel
from src.password.repositories import PasswordRepository, PasswordUrlRepository, PasswordGroupRepository
from src.password.types import PasswordDTO
from src.user.repositories import UserRepository

logger = logging.getLogger()


class PasswordService:
    @staticmethod
    def _encrypt_password_server_side(password_client_side_encrypted: bytes, iterations: int, user_id: uuid.UUID) -> bytes:

        user_repo = UserRepository()
        user_entity: UserModel = user_repo.get_by_id(user_id)
        if not user_entity:
            raise Exception(f"No user with id = {user_id}")

        fernet_crypto = CryptographyFernet()
        password_encrypted_by_server = fernet_crypto.password_encrypt(
            message=password_client_side_encrypted,
            additional_pepper=str(user_entity.password_hash),
            iterations=iterations
        )
        return password_encrypted_by_server

    @staticmethod
    def add_password_to_groups(password_groups_ids: List[uuid.UUID], password_id: uuid.UUID):
        repo = PasswordGroupRepository()
        for group_id in password_groups_ids:
            password_group_entity = repo.add_password_to_group(
                password_id=password_id,
                group_id=group_id
            )
            repo.save(password_group_entity)
        repo.commit()

    @staticmethod
    def create_password_urls(password_urls: List[str], password_id: uuid.UUID):
        repo = PasswordUrlRepository()
        for url in password_urls:
            entity = repo.create(
                url=url,
                password_id=password_id
            )
            repo.save(entity)
        repo.commit()

    @staticmethod
    def update_password_to_groups(password_groups_ids: List[uuid.UUID], password_id: uuid.UUID):
        repo = PasswordGroupRepository()
        repo.delete_password_from_all_groups(password_id=password_id)

        for group_id in password_groups_ids:
            password_group_entity = repo.add_password_to_group(
                password_id=password_id,
                group_id=group_id
            )
            repo.save(password_group_entity)
        repo.commit()

    @staticmethod
    def update_password_urls(password_urls: List[str], password_id: uuid.UUID):
        repo = PasswordUrlRepository()
        repo.delete_all_by_password_id(password_id=password_id)

        for url in password_urls:
            entity = repo.create(
                url=url,
                password_id=password_id
            )
            repo.save(entity)
        repo.commit()

    @classmethod
    def create(cls, password_details: PasswordDTO) -> PasswordModel:
        password_repo = PasswordRepository()
        server_side_password_encrypted = cls._encrypt_password_server_side(
            password_client_side_encrypted=password_details.client_side_password_encrypted,
            iterations=password_details.server_side_iterations,
            user_id=password_details.user_id
        )

        password_entity = password_repo.create(
            name=password_details.name,
            login=password_details.login,
            server_side_password_encrypted=server_side_password_encrypted,
            server_side_algo=password_details.server_side_algo,
            server_side_iterations=password_details.server_side_iterations,
            client_side_algo=password_details.client_side_algo,
            client_side_iterations=password_details.client_side_iterations,
            note=password_details.note,
            user_id=password_details.user_id
        )
        password_repo.save(password_entity)
        password_repo.commit()

        cls.create_password_urls(
            password_id=password_entity.id,
            password_urls=password_details.urls
        )

        cls.add_password_to_groups(
            password_id=password_entity.id,
            password_groups_ids=password_details.groups_ids
        )

        return password_entity

    @classmethod
    def get(cls, password_id: uuid.UUID) -> PasswordModel:
        repo = PasswordRepository()
        entity = repo.get_by_id(password_id)
        return entity

    @classmethod
    def update(cls, entity_id: uuid.UUID, password_new_details: PasswordDTO) -> PasswordModel:
        password_repo = PasswordRepository()
        server_side_password_encrypted = cls._encrypt_password_server_side(
            password_client_side_encrypted=password_new_details.client_side_password_encrypted,
            iterations=password_new_details.server_side_iterations,
            user_id=password_new_details.user_id
        )

        password_entity = password_repo.update(
            entity_id=entity_id,
            name=password_new_details.name,
            login=password_new_details.login,
            server_side_password_encrypted=server_side_password_encrypted,
            server_side_algo=password_new_details.server_side_algo,
            server_side_iterations=password_new_details.server_side_iterations,
            client_side_algo=password_new_details.client_side_algo,
            client_side_iterations=password_new_details.client_side_iterations,
            note=password_new_details.note,
            user_id=password_new_details.user_id
        )
        password_repo.save(password_entity)
        password_repo.commit()

        cls.update_password_urls(
            password_id=password_entity.id,
            password_urls=password_new_details.urls
        )

        cls.update_password_to_groups(
            password_id=password_entity,
            password_groups_ids=password_new_details.groups_ids
        )

        return password_entity

    @classmethod
    def delete(cls, password_id: uuid.UUID, user_id: uuid.UUID) -> uuid.UUID:
        # delete urls
        password_urls_repo = PasswordUrlRepository()
        password_urls_repo.delete_all_by_password_id(password_id=password_id)

        # delete from group
        password_groups_repo = PasswordGroupRepository()
        password_groups_repo.delete_password_from_all_groups(password_id=password_id)

        password_repo = PasswordRepository()
        password_repo.delete(
            password_id=password_id,
            user_id=user_id
        )
        return password_id

    @staticmethod
    def find_all_by_user(user_id: uuid.UUID) -> List[PasswordModel]:
        repo = PasswordRepository()
        entities = repo.find_all_by_user(user_id=user_id)
        return entities

    @staticmethod
    def find_all_by_group(group_id: uuid.UUID) -> List[PasswordModel]:
        repo = PasswordRepository()
        entities = repo.find_by_group_id(group_id=group_id)
        return entities
