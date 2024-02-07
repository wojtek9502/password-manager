import datetime

from src import UserModel
from src.user.services import UserService, UserTokenService
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


class UserTokenServiceTest(BaseTest):
    def test_create_user_token(self):
        # given
        service = UserTokenService()
        user_entity = create_user()
        token = 'test_token'

        # when
        token_entity = service.create_token(
            token=token,
            user_id=user_entity.id
        )

        # then
        assert token_entity.user_id == user_entity.id
        assert token_entity.token == token
        assert token_entity.expiration_date > token_entity.inserted_on

    def test_is_token_valid(self):
        # given
        service = UserTokenService()
        user_entity = create_user()
        token = 'test_token'
        service.create_token(
            token=token,
            user_id=user_entity.id
        )

        # when
        is_token_valid = service.is_token_valid(token)

        # then
        assert is_token_valid

    def test_is_token_valid_if_not_exists(self):
        # given
        service = UserTokenService()
        token = 'test_token_not_exists'

        # when
        is_token_valid = service.is_token_valid(token)

        # then
        assert not is_token_valid

    def test_delete_user_token_when_no_tokens_expired(self):
        # given
        service = UserTokenService()
        user_entity = create_user()
        token = 'test_token'

        # when
        service.create_token(
            token=token,
            user_id=user_entity.id
        )
        tokens_before_delete = service.get_all()

        # when
        service.delete_expired_tokens()
        tokens_after_delete = service.get_all()

        # then
        assert len(tokens_before_delete) == len(tokens_after_delete)

    def test_delete_user_token_when_token_expired(self):
        # given
        service = UserTokenService()
        user_entity = create_user()
        token = 'test_token'
        expiration_date_from_the_past = datetime.datetime.now() - datetime.timedelta(days=1)

        # when - create token
        service.create_token(
            token=token,
            user_id=user_entity.id,
            expiration_date=expiration_date_from_the_past
        )
        tokens_before_delete = service.get_all()

        # then
        assert len(tokens_before_delete) == 1

        # when
        service.delete_expired_tokens()
        tokens_after_delete = service.get_all()

        # then
        assert len(tokens_after_delete) == 0