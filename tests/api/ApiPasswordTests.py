import uuid

from sqlalchemy.orm import Session

from src import PasswordModel
from src.api.password.schema import PasswordCreateRequestSchema, PasswordCreateResponseSchema, \
    PasswordUpdateRequestSchema, PasswordUpdateResponseSchema, PasswordListResponseSchema
from src.password.services import PasswordService
from src.password.types import PasswordDTO
from tests.api.ApiBaseTests import ApiBaseTest
from tests.test_utils.create_db_resources import create_test_user_and_get_token


def _create_password(session: Session, user_id: uuid.UUID,
                     name: str = 'test', login: str = 'test@test.pl', password: str = 'pass') -> PasswordModel:
    password_service = PasswordService(session=session)
    password_dto: PasswordDTO = PasswordDTO(
            name=name,
            login=login,
            server_side_algo='Fernet',
            server_side_iterations=600_000,
            password_encrypted=password.encode(),
            client_side_algo='Fernet',
            client_side_iterations=600_000,
            note='',
            urls=[],
            groups=[],
            user_id=user_id
        )
    password_entity = password_service.create(password_details=password_dto)
    return password_entity


class ApiPasswordTests(ApiBaseTest):
    def test_list_password(self):
        # given
        user_id, user_token = create_test_user_and_get_token(session=self.session)
        password_entity1 = _create_password(session=self.session, user_id=user_id, name='password1', login='test1')
        password_entity2 = _create_password(session=self.session, user_id=user_id, name='password2', login='test2')

        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }

        # when
        response = self.test_api.get(
            url="/password/list",
            headers=headers
        )
        response_json = response.json()
        response_data: PasswordListResponseSchema = PasswordListResponseSchema.model_validate(response_json)

        # then
        assert len(response_data.passwords) == 2
        assert response_data.passwords[0].name == password_entity1.name
        assert response_data.passwords[0].login == password_entity1.login
        assert response_data.passwords[1].name == password_entity2.name
        assert response_data.passwords[1].login == password_entity2.login

    def test_create_password(self):
        # given
        user_id, user_token = create_test_user_and_get_token(session=self.session)
        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }

        name = 'test'
        login = 'test@test.pl'
        client_password_encrypted = 'test'
        urls = ['www.a.pl']
        password_dto = PasswordCreateRequestSchema(
            name=name,
            login=login,
            password_encrypted=client_password_encrypted,
            client_side_algo='fernet',
            client_side_iterations=600_000,
            note='',
            urls=urls,
            groups_ids=[]
        )
        payload = password_dto.model_dump()

        # when
        response = self.test_api.post(
            url="/password/create",
            headers=headers,
            json=payload
        )
        response_json = response.json()
        password_data = PasswordCreateResponseSchema.model_validate(response_json)

        # then
        assert password_data.name == name
        assert password_data.login == login
        assert password_data.groups_ids == []
        assert password_data.urls == urls

    def test_update_password(self):
        # given
        password_service = PasswordService(session=self.session)
        user_id, user_token = create_test_user_and_get_token(session=self.session)
        password_entity = _create_password(session=self.session, user_id=user_id)
        password_id = str(password_entity.id)
        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }

        new_name = 'test2'
        new_login = 'test2@test.pl'
        new_client_password_encrypted = 'test2'
        new_urls = ['www.b2.pl']
        password_dto = PasswordUpdateRequestSchema(
            password_id=password_id,
            name=new_name,
            login=new_login,
            password_encrypted=new_client_password_encrypted,
            client_side_algo='fernet',
            client_side_iterations=600_000,
            note='',
            urls=new_urls,
            groups_ids=[]
        )
        payload = password_dto.model_dump()
        payload['password_id'] = password_id

        # when
        response = self.test_api.post(
            url="/password/update",
            headers=headers,
            json=payload
        )
        response_json = response.json()
        password_data = PasswordUpdateResponseSchema.model_validate(response_json)
        password_db_entity = password_service.get_user_password_dto(password_id=password_entity.id)

        # then
        assert password_data.name == new_name
        assert password_data.login == new_login
        assert password_data.groups_ids == []
        assert password_data.urls == new_urls
        assert len(password_db_entity.history)

    def test_delete_password(self):
        # given
        password_service = PasswordService(session=self.session)
        user_id, user_token = create_test_user_and_get_token(session=self.session)
        password_entity = _create_password(session=self.session, user_id=user_id)
        password_id = str(password_entity.id)
        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }
        payload = dict(
            password_id=password_id
        )

        # when
        self.test_api.delete(
            url="/password/delete",
            headers=headers,
            params=payload
        )
        user_passwords = password_service.get_user_passwords_dtos(user_id=user_id)

        # then
        assert not len(user_passwords)