import uuid

import pytest
from sqlalchemy.exc import NoResultFound

from src.user.repositories import UserRepository
from tests.BaseTest import BaseTest


class UserRepositoryTest(BaseTest):
    def test_create_user(self):
        # given
        repo = UserRepository(session=self.session)
        username = 'admin'
        password = 'admin'

        # when
        entity = repo.create(
            username=username,
            password_clear=password,

        )
        repo.save(entity)
        repo.commit()
        user_entity = repo.find_by_username(username=username)

        # then
        assert user_entity.username == username

    def test_find_by_username(self):
        # given
        repo = UserRepository(session=self.session)
        username = 'admin'

        # when
        entity = repo.create(
            username=username,
            password_clear='admin',
        )
        entity_id = entity.id
        repo.save(entity)
        repo.commit()

        # when
        found_entity = repo.find_by_username(username=username)

        # then
        assert entity_id == found_entity.id
        assert len(repo.find_all()) == 1

    def test_find_by_not_existing_username(self):
        # given
        repo = UserRepository(session=self.session)
        username = 'admin_not_exists'

        # when
        with pytest.raises(NoResultFound) as exc_info:
            repo.find_by_username(username=username)

        # then
        assert isinstance(exc_info.value, NoResultFound)

    def test_find_by_user_id(self):
        # given
        repo = UserRepository(session=self.session)
        username = 'admin'

        # when
        entity = repo.create(
            username=username,
            password_clear='admin',
        )
        entity_id = entity.id
        repo.save(entity)
        repo.commit()

        # when
        found_entity = repo.find_by_id(user_id=entity_id)

        # then
        assert entity_id == found_entity.id
        assert len(repo.find_all()) == 1

    def test_find_by_not_existing_user_id(self):
        # given
        repo = UserRepository(session=self.session)
        user_id = uuid.UUID('0f0d98c1-5576-4756-8058-f3eaf4cf33ca')

        # when
        with pytest.raises(NoResultFound) as exc_info:
            repo.find_by_id(user_id=user_id)

        # then
        assert isinstance(exc_info.value, NoResultFound)

    def test_update_user(self):
        # given
        repo = UserRepository(session=self.session)
        origin_username = 'admin'
        updated_username = 'admin_updated'
        origin_password = 'password'
        updated_password = 'password_new'

        # when
        entity = repo.create(
            username=origin_username,
            password_clear=origin_password
        )
        user_old_password_hash = entity.password_hash
        repo.save(entity)
        repo.commit()

        # then
        assert entity.username == origin_username

        # when
        repo.update(
            entity=entity,
            username=updated_username,
            password_clear=updated_password,
        )
        user_new_password_hash = entity.password_hash

        # then
        assert entity.username == updated_username
        assert user_old_password_hash != user_new_password_hash

    def test_delete_user_by_uuid(self):
        # given
        repo = UserRepository(session=self.session)
        username = 'admin'

        # when
        entity = repo.create(
            username=username,
            password_clear='admin',
        )
        entity_id = entity.id
        repo.save(entity)
        repo.commit()

        # when
        deleted_entity_id = repo.delete_by_uuid(user_uuid=entity_id)

        # then
        assert entity_id == deleted_entity_id
        assert len(repo.find_all()) == 0
