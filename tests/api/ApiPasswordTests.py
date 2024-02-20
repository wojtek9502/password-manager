import os
import uuid

from sqlalchemy.orm import Session

from src.password.services import PasswordService
from src.user.services import UserService
from tests.api.ApiBaseTests import ApiBaseTest


def _create_test_user_and_get_token(session: Session, user: str = 'test', password_clear: str = 'test') -> str:
    service = UserService(session=session)
    service.create_user(username=user, password_clear=password_clear)
    user_token = service.login_user(username=user, password_clear=password_clear)
    return user_token


class ApiPasswordTests(ApiBaseTest):
    def test_create_password(self):
        # given
        password_service = PasswordService(session=self.session)
        user_token = _create_test_user_and_get_token(session=self.session)
        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }

        # when
        response = self.test_api.get(
            url="/user/",
            headers=headers
        )
        response_json = response.json()

        # then
        assert response_json[0]['id'] == str(entity.id)
        assert response_json[0]['username'] == username
