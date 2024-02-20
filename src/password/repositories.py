import uuid
from typing import List

from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

from src import GroupModel
from src.common.BaseRepository import BaseRepository, NotFoundEntityError
from src.password.models import PasswordModel, PasswordUrlModel, PasswordGroupModel, PasswordHistoryModel


class PasswordRepository(BaseRepository):
    def model_class(self):
        return PasswordModel

    def create(self, name: str, login: str, server_side_password_encrypted: bytes, server_side_algo: str,
               server_side_iterations: int, client_side_algo: str, client_side_iterations: int,
               note: str, user_id: uuid.UUID) -> PasswordModel:        
        entity = PasswordModel(
            name=name,
            login=login,
            password_encrypted=server_side_password_encrypted,
            server_side_algo=server_side_algo,
            server_side_iterations=server_side_iterations,
            client_side_algo=client_side_algo,
            client_side_iterations=client_side_iterations,
            note=note,
            user_id=user_id,
        )
        return entity

    def update(self, entity_id: uuid.UUID, name: str, login: str, server_side_password_encrypted: bytes,
               server_side_algo: str, server_side_iterations: int, client_side_algo: str, client_side_iterations: int,
               note: str, user_id: uuid.UUID) -> PasswordModel:
        entity: PasswordModel = self.get_by_id(entity_id)
        entity.name = name
        entity.login = login
        entity.password_encrypted = server_side_password_encrypted
        entity.server_side_algo = server_side_algo
        entity.server_side_iterations = server_side_iterations
        entity.client_side_algo = client_side_algo
        entity.client_side_iterations = client_side_iterations
        entity.note = note
        entity.user_id = user_id
        return entity

    def find_all_by_user(self, user_id: uuid.UUID) -> List[PasswordModel]:
        try:
            entities = self.query().filter(PasswordModel.user_id == user_id).all()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entities

    def find_by_group_id(self, group_id: uuid.UUID) -> PasswordModel:
        try:
            entity = self.query().filter(PasswordModel.id == group_id).one()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entity

    def delete(self, password_id: uuid.UUID, user_id: uuid.UUID) -> uuid.UUID:
        query = self.query().filter(PasswordModel.id == password_id)
        entity = query.one_or_none()
        if not entity:
            raise NotFoundEntityError(f"Not found password with uuid: {password_id} for user {user_id}")
        entity_uuid = entity.id

        try:
            query.delete()
            self.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

        return entity_uuid


class PasswordUrlRepository(BaseRepository):
    def model_class(self):
        return PasswordUrlModel

    def create(self, url: str, password_id: uuid.UUID) -> PasswordUrlModel:
        entity = PasswordUrlModel(
            url=url,
            password_id=password_id
        )
        return entity

    def update(self, entity_id: uuid.UUID, url: str) -> PasswordUrlModel:
        entity: PasswordUrlModel = self.get_by_id(entity_id)
        entity.url = url
        return entity

    def find_by_id(self, password_url_id: uuid.UUID) -> PasswordUrlModel:
        try:
            entity = self.query().filter(PasswordUrlModel.id == password_url_id).one()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entity

    def find_all_by_password_id(self, password_id: uuid.UUID) -> List[PasswordUrlModel]:
        try:
            entities = self.query().filter(PasswordUrlModel.password_id == password_id).all()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entities

    def delete(self, password_url_id: uuid.UUID) -> uuid.UUID:
        query = self.query().filter(PasswordUrlModel.id == password_url_id) 
        entity = query.one_or_none()
        if entity:
            entity_uuid = entity.id

            try:
                query.delete()
                self.commit()
            except SQLAlchemyError as e:
                self.session.rollback()
                raise e

            return entity_uuid

    def delete_all_by_password_id(self, password_id: uuid.UUID) -> List[uuid.UUID]:
        query = self.query().filter(PasswordUrlModel.password_id == password_id) 
        entities: List[PasswordUrlModel] = query.all()
        deleted_entities_ids = []

        for password_url_entity in entities:
            try:
                query.delete()
                self.commit()
                deleted_entities_ids.append(password_url_entity.id)
            except SQLAlchemyError as e:
                self.session.rollback()
                raise e

        return deleted_entities_ids


class PasswordHistoryRepository(BaseRepository):
    def model_class(self):
        return PasswordHistoryModel

    def create(self, name: str, login: str, client_side_password_encrypted: bytes,
               client_side_algo: str, client_side_iterations: int,
               note: str, user_id: uuid.UUID, password_id: uuid.UUID) -> PasswordHistoryModel:
        entity = PasswordHistoryModel(
            name=name,
            login=login,
            client_side_password_encrypted=client_side_password_encrypted,
            client_side_algo=client_side_algo,
            client_side_iterations=client_side_iterations,
            note=note,
            user_id=user_id,
            password_id=password_id
        )
        return entity

    def find_all_by_password_id(self, password_id: uuid.UUID) -> List[PasswordHistoryModel]:
        try:
            entities = self.query().filter(PasswordHistoryModel.password_id == password_id).all()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
        return entities

    def delete(self, password_history_id: uuid.UUID) -> uuid.UUID:
        query = self.query().filter(PasswordHistoryModel.id == password_history_id)
        entity = query.one_or_none()
        if entity:
            entity_uuid = entity.id

            try:
                query.delete()
                self.commit()
            except SQLAlchemyError as e:
                self.session.rollback()
                raise e

            return entity_uuid

    def delete_all_by_password_id(self, password_id: uuid.UUID) -> List[uuid.UUID]:
        query = self.query().filter(PasswordHistoryModel.password_id == password_id)
        entities: List[PasswordUrlModel] = query.all()
        deleted_entities_ids = []

        for password_history_entity in entities:
            try:
                query.delete()
                self.commit()
                deleted_entities_ids.append(password_history_entity.id)
            except SQLAlchemyError as e:
                self.session.rollback()
                raise e

        return deleted_entities_ids


class PasswordGroupRepository(BaseRepository):
    def model_class(self):
        return PasswordGroupModel

    def add_password_to_group(self, password_id: uuid.UUID, group_id: uuid.UUID) -> PasswordGroupModel:
        entity = PasswordGroupModel(
            group_id=group_id,
            password_id=password_id
        )
        return entity

    def delete_password_from_group(self, password_id: uuid.UUID, group_id: uuid.UUID) -> uuid.UUID:
        query = self.query().filter(
            and_(
                PasswordGroupModel.id == password_id,
                PasswordGroupModel.group_id == group_id,
            )
        )
        entity = query.one_or_none()
        if entity:
            entity_uuid = entity.id

            try:
                query.delete()
                self.commit()
            except SQLAlchemyError as e:
                self.session.rollback()
                raise e

            return entity_uuid

    def delete_password_from_all_groups(self, password_id: uuid.UUID) -> List[uuid.UUID]:
        query = self.query().filter(PasswordGroupModel.password_id == password_id)
        entities: List[PasswordGroupModel] = query.all()
        deleted_password_ids = []

        for password_group_entity in entities:
            try:
                query.delete()
                self.commit()
                deleted_password_ids.append(password_group_entity.password_id)
            except SQLAlchemyError as e:
                self.session.rollback()
                raise e

        return deleted_password_ids

    @staticmethod
    def find_password_groups(password_entity: PasswordModel) -> List[GroupModel]:
        return password_entity.groups
