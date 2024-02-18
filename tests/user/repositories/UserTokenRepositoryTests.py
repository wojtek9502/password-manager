import datetime

from sqlalchemy.orm import Session

from src import UserModel
from src.user.repositories import UserTokenRepository
from src.user.services import UserService
from tests.BaseTest import BaseTest


def create_user(session: Session) -> UserModel:
    service = UserService(session=session)
    username = 'admin'
    password_clear = 'password'

    user_entity = service.create_user(
        username=username,
        password_clear=password_clear,
    )
    return user_entity


class UserRepositoryTest(BaseTest):
    def test_create_user_token(self):
        # given
        repo = UserTokenRepository(session=self.session)
        user_entity = create_user(session=self.session)
        token_value = 'token'

        # when
        entity = repo.create(
            token=token_value,
            user_id=user_entity.id

        )
        repo.save(entity)
        repo.commit()
        token_entity = repo.find_by_token(token=token_value)

        # then
        assert token_entity.user_id == user_entity.id
        assert token_entity.token == token_value
        assert token_entity.inserted_on
        assert token_entity.expiration_date > token_entity.inserted_on

    def test_delete_user_token_when_no_tokens_expired(self):
        # given
        repo = UserTokenRepository(session=self.session)
        user_entity = create_user(session=self.session)
        token_value = 'token'

        token_entity = repo.create(
            token=token_value,
            user_id=user_entity.id

        )
        repo.save(token_entity)
        repo.commit()
        tokens_before_delete = repo.find_all()

        # when
        repo.delete_expired_tokens()
        tokens_after_delete = repo.find_all()

        # then
        assert len(tokens_before_delete) == len(tokens_after_delete)

    def test_delete_user_token_when_token_expired(self):
        # given
        repo = UserTokenRepository(session=self.session)
        user_entity = create_user(session=self.session)
        token_value = 'token'
        expiration_date_from_the_past = datetime.datetime.now() - datetime.timedelta(days=1)

        # when - create token
        token_entity = repo.create(
            token=token_value,
            user_id=user_entity.id,
            expiration_date=expiration_date_from_the_past

        )
        repo.save(token_entity)
        repo.commit()
        tokens_before_delete = repo.find_all()

        # then
        assert len(tokens_before_delete) == 1

        # when
        repo.delete_expired_tokens()
        tokens_after_delete = repo.find_all()

        # then
        assert len(tokens_after_delete) == 0
