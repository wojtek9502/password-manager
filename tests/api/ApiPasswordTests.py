import os
import uuid

from src.api.password.schema import PasswordCreateRequestSchema, PasswordCreateResponseSchema, \
    PasswordUpdateRequestSchema, PasswordUpdateResponseSchema, PasswordListResponseSchema, PasswordHistoryResponseSchema
from src.group.repositories import GroupRepository
from src.password.services import PasswordService
from src.password.utils import _decrypt_password_server_side, create_password_dto
from tests.api.ApiBaseTests import ApiBaseTest
from tests.test_utils.create_db_resources import create_test_user_and_get_token, create_password, \
    create_password_history


class ApiPasswordTests(ApiBaseTest):
    def test_password_list(self):
        # given
        user_id, user_token = create_test_user_and_get_token(session=self.session)
        password_entity1 = create_password(session=self.session, user_id=user_id, name='password1', login='test1')
        password_entity2 = create_password(session=self.session, user_id=user_id, name='password2', login='test2')

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

    def test_password_list_with_master_token(self):
        # given
        user_token = os.environ['API_AUTH_MASTER_TOKEN']

        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }

        # when
        response = self.test_api.get(
            url="/password/list",
            headers=headers
        )

        # then
        assert response.status_code == 400
        
    def test_password_history_list(self):
        # given
        user_id, user_token = create_test_user_and_get_token(session=self.session)

        # given create password and password history
        password_entity = create_password(session=self.session, user_id=user_id, name='password_name_1', login='test1')
        password_client_side_encrypted = _decrypt_password_server_side(
            session=self.session,
            password_server_side_encrypted=password_entity.password_encrypted,
            user_id=user_id
        )
        password_dto = create_password_dto(
            password_entity=password_entity,
            password_client_side_encrypted=password_client_side_encrypted
        )
        password_history = create_password_history(
            db_session=self.session,
            password_id=password_entity.id,
            password_details=password_dto
        )

        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }

        # when
        response = self.test_api.get(
            url=f"/password/{password_entity.id}/history",
            headers=headers
        )
        response_json = response.json()
        password_history_response = [PasswordHistoryResponseSchema.model_validate(item) for item in response_json]

        # then
        assert len(password_entity.history) == 1
        assert len(password_history_response) == 1
        assert password_history_response[0].name == password_history.name

    def test_password_history_list_when_password_not_belong_to_user(self):
        # given
        user1_id, user1_token = create_test_user_and_get_token(session=self.session, user='user1', password_clear='user1')
        user2_id, user2_token = create_test_user_and_get_token(session=self.session, user='user2', password_clear='user2')

        # given create password and password history
        user1_password = create_password(session=self.session, user_id=user1_id, name='password_name_1', login='test1')
        password_client_side_encrypted = _decrypt_password_server_side(
            session=self.session,
            password_server_side_encrypted=user1_password.password_encrypted,
            user_id=user1_id
        )
        user1_password_dto = create_password_dto(
            password_entity=user1_password,
            password_client_side_encrypted=password_client_side_encrypted
        )
        create_password_history(
            db_session=self.session,
            password_id=user1_password.id,
            password_details=user1_password_dto
        )

        headers = {
            "X-API-KEY": user2_token,
            'Accept': 'application/json'
        }

        # when
        response = self.test_api.get(
            url=f"/password/{user1_password.id}/history",
            headers=headers
        )
        response_json = response.json()

        # then
        assert response.status_code == 400
        assert 'Password not belongs to user' in response_json['detail']

    def test_create_password(self):
        # given
        user_id, user_token = create_test_user_and_get_token(session=self.session, user='test2')
        user_default_group = GroupRepository(session=self.session).find_user_default_group(user_id=user_id)
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
        assert password_data.groups_ids == [user_default_group.id]
        assert password_data.urls == urls

    def test_update_password(self):
        # given
        password_service = PasswordService(session=self.session)
        user_id, user_token = create_test_user_and_get_token(session=self.session)
        password_entity = create_password(session=self.session, user_id=user_id)
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
        password_entity = create_password(session=self.session, user_id=user_id)
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

    def test_delete_password_when_password_not_exists(self):
        # given
        user_id, user_token = create_test_user_and_get_token(session=self.session)
        password_id = str(uuid.uuid4())
        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }
        payload = dict(
            password_id=password_id
        )

        # when
        request = self.test_api.delete(
            url="/password/delete",
            headers=headers,
            params=payload
        )

        # then
        assert request.status_code == 400
        assert 'Not found password' in request.json()['detail']