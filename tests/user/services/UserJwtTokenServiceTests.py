import pytest

from sqlalchemy.exc import NoResultFound

from src import UserModel
from src.user.services import UserJwtTokenService, UserService
from tests.BaseTest import BaseTest


def create_user() -> UserModel:
    service = UserService()
    username = 'admin'
    password_clear = 'password'

    user_entity = service.create_user(
        username=username,
        password_clear=password_clear,
    )
    return user_entity


class UserJwtTokenServiceTests(BaseTest):
    def test_create_token(self):
        # given
        user_entity = create_user()
        token_service = UserJwtTokenService()
        username = user_entity.username

        # when
        token_str = token_service.create(
            username=username
        )

        # then
        assert token_str

    def test_create_token_for_empty_user(self):
        # given
        token_service = UserJwtTokenService()
        username = ''

        # when
        token_str = token_service.create(
            username=username
        )

        # then
        assert token_str is None

    def test_create_and_token_validation(self):
        # given
        user_entity = create_user()
        token_service = UserJwtTokenService()
        username = user_entity.username

        # when - create token
        token_str = token_service.create(
            username=username
        )

        # then
        assert token_str

        # when - check is token valid
        is_token_valid = token_service.is_valid(
            jwt_token=token_str,
            username=username
        )

        assert is_token_valid is True

    def test_create_and_token_validation_when_token_invalid(self):
        # given
        user_entity = create_user()
        token_service = UserJwtTokenService()
        username = user_entity.username
        invalid_token = 'abcd'

        # when - check is token valid
        is_token_valid = token_service.is_valid(
            jwt_token=invalid_token,
            username=username
        )

        assert is_token_valid is False

    def test_token_valid_with_empty_user(self):
        # given
        username = ''
        token = 'token_123'
        token_service = UserJwtTokenService()

        # when - check is token valid, not existing user
        is_token_valid = token_service.is_valid(
            jwt_token=token,
            username=username
        )

        # then
        assert is_token_valid is False

    def test_token_valid_without_existing_user(self):
        # given
        username = 'not exist'
        token = 'token_123'
        token_service = UserJwtTokenService()

        # when - check is token valid, not existing user
        with pytest.raises(NoResultFound) as exc_info:
            token_service.is_valid(
                jwt_token=token,
                username=username
            )

        # then
        assert isinstance(exc_info.value, NoResultFound)

    def test_token_decode(self):
        # given
        user_entity = create_user()
        token_service = UserJwtTokenService()
        username = user_entity.username

        token_str = token_service.create(
            username=username
        )
        # when
        token_decoded = token_service.decode(
            jwt_token=token_str,
            username=username
        )

        # then
        assert token_decoded.username == username
