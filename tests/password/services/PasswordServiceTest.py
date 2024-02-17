import uuid

import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.common.BaseRepository import NotFoundEntityError
from src.password.services import PasswordService
from src.password.types import PasswordDTO
from src.user.exceptions import UserLoginPasswordInvalidError
from src.user.repositories import UserRepository
from src.user.services import UserService
from tests.BaseTest import BaseTest
from tests.password.utils import mock_client_side_password_encrypted, mock_password_group


class PasswordServiceTest(BaseTest):
    def test_create_password(self):
        # given
        service = PasswordService()
        name = 'test password'
        login = 'test@test.pl'
        client_site_iterations = 600_000

        # client side password
        client_side_password_encrypted = mock_client_side_password_encrypted()

        # password groups
        group1_id = mock_password_group('group1').id
        groups_ids = [group1_id]

        # password urls
        password_urls = ['https://website1.pl', 'https://website2.pl']

        password_details: PasswordDTO = PasswordDTO(
            name=name,
            login=login,
            server_side_algo='Fernet',
            server_side_iterations=600_000,
            client_side_password_encrypted=client_side_password_encrypted,
            client_side_algo='Fernet',
            client_side_iterations=client_site_iterations,
            note='',
            urls=password_urls,
            groups_ids=groups_ids,
            user_id=user_id
        )

        # when
        password_entity = service.create(
            password_details=password_details
        )
        password_groups_names = [group.name for group in password_entity.groups]

        # then
        assert password_groups_names == groups_ids
        assert user_entity.password_hash != password_clear

    def test_find_all_users(self):
        # given
        service = UserService()
        username = 'admin'
        password_clear = 'password'

        service.create_user(
            username=username,
            password_clear=password_clear
        )

        # when
        user_entities = service.find_all()

        assert len(user_entities) == 1

    def test_find_user_by_username(self):
        # given
        service = UserService()
        username = 'admin'
        password_clear = 'password'

        service.create_user(
            username=username,
            password_clear=password_clear
        )

        # when
        user_entity = service.find_by_username(username=username)

        assert user_entity.username == username

    def test_find_user_by_username_when_user_not_exists(self):
        # given
        service = UserService()
        username = 'not_exist'

        with pytest.raises(NoResultFound) as exc_info:
            service.find_by_username(username)

        # then
        assert isinstance(exc_info.value, NoResultFound)

    def test_login_user(self):
        # given
        service = UserService()
        username = 'admin'
        password_clear = 'password'

        service.create_user(
            username=username,
            password_clear=password_clear
        )

        # when
        jwt_token = service.login_user(
            username=username,
            password_clear=password_clear
        )

        # then
        assert jwt_token

    def test_login_user_wrong_password(self):
        # given
        service = UserService()
        username = 'admin'
        password_clear = 'password'

        service.create_user(
            username=username,
            password_clear=password_clear,
        )

        # when
        with pytest.raises(UserLoginPasswordInvalidError) as exc_info:
            service.login_user(
                username=username,
                password_clear='wrong_password'
            )

        # then
        assert isinstance(exc_info.value, UserLoginPasswordInvalidError)

    def test_login_user_not_exists(self):
        # given
        service = UserService()
        username = 'not_exists'
        password_clear = 'not_exists'

        # when
        with pytest.raises(UserLoginPasswordInvalidError) as exc_info:
            service.login_user(
                username=username,
                password_clear=password_clear
            )

        # then
        assert isinstance(exc_info.value, UserLoginPasswordInvalidError)

    def test_create_existing_user(self):
        # given
        service = UserService()
        username = 'admin'
        password_clear = 'password'

        service.create_user(
            username=username,
            password_clear=password_clear,
        )

        # when - create the same user again
        with pytest.raises(IntegrityError) as exc_info:
            service.create_user(
                username=username,
                password_clear=password_clear,
            )

        # then
        assert isinstance(exc_info.value, IntegrityError)

    def test_update_user(self):
        # given
        service = UserService()
        username = 'admin'
        password_clear = 'password'
        new_token = 'new_token'

        user_entity = service.create_user(
            username=username,
            password_clear=password_clear,
        )

        # when
        updated_entity = service.update_user(
            user_id=user_entity.id,
            password_clear=password_clear,
        )

        # then
        assert updated_entity.username == username

    def test_update_not_existing_user(self):
        # given
        service = UserService()
        not_existing_user_id = uuid.UUID('0f0d98c1-5576-4756-8058-f3eaf4cf33ca')

        # when
        with pytest.raises(NotFoundEntityError) as exc_info:
            service.update_user(
                user_id=not_existing_user_id,
                password_clear='new_pass',
            )

        # then
        assert isinstance(exc_info.value, NotFoundEntityError)

    def test_delete_user(self):
        # given
        repo = UserRepository()
        service = UserService()
        username = 'admin'
        password_clear = 'password'

        user_entity = service.create_user(
            username=username,
            password_clear=password_clear,
        )
        user_id = user_entity.id

        # when
        deleted_user_id = service.delete_user(
            user_id=user_entity.id,
        )

        # then
        assert deleted_user_id == user_id
        assert len(repo.find_all()) == 0

    def test_delete_not_existing_user(self):
        # given
        service = UserService()
        not_existing_user_id = uuid.UUID('0f0d98c1-5576-4756-8058-f3eaf4cf33ca')

        # when
        with pytest.raises(NotFoundEntityError) as exc_info:
            service.delete_user(
                user_id=not_existing_user_id,
            )

        # then
        assert isinstance(exc_info.value, NotFoundEntityError)

    def test_delete_not_existing_user_by_username(self):
        # given
        service = UserService()
        not_existing_user_id = uuid.UUID('0f0d98c1-5576-4756-8058-f3eaf4cf33ca')

        # when
        with pytest.raises(NotFoundEntityError) as exc_info:
            service.delete_user(
                user_id=not_existing_user_id,
            )

        # then
        assert isinstance(exc_info.value, NotFoundEntityError)