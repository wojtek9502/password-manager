import logging
import uuid
from typing import List

from src.common.BaseService import BaseService
from src.password.models import PasswordModel, PasswordHistoryModel
from src.password.repositories import PasswordRepository, PasswordUrlRepository, PasswordGroupRepository, \
    PasswordHistoryRepository
from src.password.types import PasswordDTO, PasswordHistoryDTO
from src.password.utils import _decrypt_password_server_side, _encrypt_password_server_side

logger = logging.getLogger()


class PasswordService(BaseService):
    def add_password_to_groups(self, password_groups_ids: List[uuid.UUID], password_id: uuid.UUID):
        repo = PasswordGroupRepository(session=self.session)
        for group_id in password_groups_ids:
            password_group_entity = repo.add_password_to_group(
                password_id=password_id,
                group_id=group_id
            )
            repo.save(password_group_entity)
        repo.commit()

    def create_password_urls(self, password_urls: List[str], password_id: uuid.UUID):
        repo = PasswordUrlRepository(session=self.session)
        for url in password_urls:
            entity = repo.create(
                url=url,
                password_id=password_id
            )
            repo.save(entity)
        repo.commit()

    def update_password_to_groups(self, password_groups_ids: List[uuid.UUID], password_id: uuid.UUID):
        repo = PasswordGroupRepository(session=self.session)
        repo.delete_password_from_all_groups(password_id=password_id)

        for group_id in password_groups_ids:
            password_group_entity = repo.add_password_to_group(
                password_id=password_id,
                group_id=group_id
            )
            repo.save(password_group_entity)
        repo.commit()

    def update_password_urls(self, password_urls: List[str], password_id: uuid.UUID):
        repo = PasswordUrlRepository(session=self.session)
        repo.delete_all_by_password_id(password_id=password_id)

        for url in password_urls:
            entity = repo.create(
                url=url,
                password_id=password_id
            )
            repo.save(entity)
        repo.commit()

    def create(self, password_details: PasswordDTO) -> PasswordModel:
        password_repo = PasswordRepository(session=self.session)
        server_side_password_encrypted = _encrypt_password_server_side(
            session=self.session,
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

        self.create_password_urls(
            password_id=password_entity.id,
            password_urls=password_details.urls
        )

        self.add_password_to_groups(
            password_id=password_entity.id,
            password_groups_ids=password_details.groups_ids
        )

        return password_entity

    def create_password_history_entity(self, password_history_details: PasswordHistoryDTO) -> PasswordHistoryModel:
        password_history_service = PasswordHistoryService(session=self.session)
        entity = password_history_service.create(password_history_details=password_history_details)
        return entity

    def get(self, password_id: uuid.UUID) -> PasswordModel:
        repo = PasswordRepository(session=self.session)
        entity: PasswordModel = repo.get_by_id(password_id)
        password_server_side_encrypted = entity.password_encrypted

        entity.password_encrypted = _decrypt_password_server_side(
            session=self.session,
            password_server_side_encrypted=password_server_side_encrypted,
            user_id=entity.user_id
        )
        return entity

    def get_all_by_user_id(self, user_id: uuid.UUID) -> List[PasswordModel]:
        repo = PasswordRepository(session=self.session)
        entities: List[PasswordModel] = repo.find_all_by_user(user_id=user_id)
        entities_with_encrypted_server_side = []

        for password_entity in entities:
            password_server_side_encrypted = password_entity.password_encrypted
            password_client_side = _decrypt_password_server_side(
                session=self.session,
                password_server_side_encrypted=password_server_side_encrypted,
                user_id=password_entity.user_id
            )
            password_entity.password_encrypted = password_client_side
            entities_with_encrypted_server_side.append(password_entity)
        return entities_with_encrypted_server_side

    def _password_update_prepare_password_history_dto(self, old_password_entity: PasswordModel,
                                                      user_id: uuid.UUID) -> PasswordHistoryDTO:
        client_side_password_encrypted = _decrypt_password_server_side(
            session=self.session,
            password_server_side_encrypted=old_password_entity.password_encrypted,
            user_id=user_id
        )

        password_history_data = PasswordHistoryDTO(
            name=old_password_entity.name,
            login=old_password_entity.login,
            client_side_password_encrypted=client_side_password_encrypted,
            client_side_algo=old_password_entity.client_side_algo,
            client_side_iterations=old_password_entity.client_side_iterations,
            note=old_password_entity.note,
            user_id=old_password_entity.user_id,
            password_id=old_password_entity.id
        )
        return password_history_data

    def update(self, entity_id: uuid.UUID, password_new_details: PasswordDTO) -> PasswordModel:
        password_repo = PasswordRepository(session=self.session)
        old_password_entity = password_repo.get_by_id(entity_id)
        old_password_dto = self._password_update_prepare_password_history_dto(
            old_password_entity=old_password_entity,
            user_id=password_new_details.user_id
        )

        server_side_password_encrypted = _encrypt_password_server_side(
            session=self.session,
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

        self.update_password_urls(
            password_id=password_entity.id,
            password_urls=password_new_details.urls
        )

        self.update_password_to_groups(
            password_id=password_entity.id,
            password_groups_ids=password_new_details.groups_ids
        )

        self.create_password_history_entity(
            password_history_details=old_password_dto
        )

        return password_entity

    def delete(self, password_id: uuid.UUID, user_id: uuid.UUID) -> uuid.UUID:
        # delete urls
        password_urls_repo = PasswordUrlRepository(session=self.session)
        password_urls_repo.delete_all_by_password_id(password_id=password_id)

        # delete from group
        password_groups_repo = PasswordGroupRepository(session=self.session)
        password_groups_repo.delete_password_from_all_groups(password_id=password_id)

        # delete history_entities
        password_groups_repo = PasswordHistoryRepository(session=self.session)
        password_groups_repo.delete_all_by_password_id(password_id=password_id)

        password_repo = PasswordRepository(session=self.session)
        password_repo.delete(
            password_id=password_id,
            user_id=user_id
        )
        return password_id


class PasswordHistoryService(BaseService):
    def create(self, password_history_details: PasswordHistoryDTO) -> PasswordHistoryModel:
        password_history_repo = PasswordHistoryRepository(session=self.session)

        password_history_entity = password_history_repo.create(
            name=password_history_details.name,
            login=password_history_details.login,
            client_side_password_encrypted=password_history_details.client_side_password_encrypted,
            client_side_algo=password_history_details.client_side_algo,
            client_side_iterations=password_history_details.client_side_iterations,
            note=password_history_details.note,
            user_id=password_history_details.user_id,
            password_id=password_history_details.password_id
        )
        password_history_repo.save(password_history_entity)
        password_history_repo.commit()

        return password_history_entity

    def delete(self, password_history_id: uuid.UUID) -> uuid.UUID:
        repo = PasswordHistoryRepository(session=self.session)
        entity_id = repo.delete(password_history_id=password_history_id)
        return entity_id

    def delete_all_by_password_id(self, password_id: uuid.UUID) -> List[uuid.UUID]:
        repo = PasswordHistoryRepository(session=self.session)
        deleted_entities_ids = repo.delete_all_by_password_id(password_id=password_id)
        return deleted_entities_ids

    def get_all_by_password_id(self, password_id: uuid.UUID) -> List[PasswordHistoryModel]:
        repo = PasswordHistoryRepository(session=self.session)
        entities = repo.find_all_by_password_id(password_id=password_id)
        entities_with_encrypted_server_side = []

        for password_history_entity in entities:
            password_server_side_encrypted = password_history_entity.password_encrypted
            password_client_side = _decrypt_password_server_side(
                session=self.session,
                password_server_side_encrypted=password_server_side_encrypted,
                user_id=password_history_entity.password.user_id
            )

            password_history_entity.password_encrypted = password_client_side
            entities_with_encrypted_server_side.append(password_history_entity)
        return entities_with_encrypted_server_side

