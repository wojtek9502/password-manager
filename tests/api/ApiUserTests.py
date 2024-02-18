import os
import uuid

from src.user.services import UserService
from tests.api.ApiBaseTests import ApiBaseTest


class ApiUsersTest(ApiBaseTest):
    def test_get_users(self):
        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }
        expected_response = []

        # when
        response = self.test_api.get(
            url="/user/",
            headers=headers
        )
        response_json = response.json()

        # then
        assert response_json == expected_response

    def test_get_users_that_exists(self):
        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }

        # given - create user
        username = 'test'
        service = UserService(session=self.session)
        entity = service.create_user(
            username=username,
            password_clear='test'
        )

        # when
        response = self.test_api.get(
            url="/user/",
            headers=headers
        )
        response_json = response.json()

        # then
        assert response_json[0]['id'] == str(entity.id)
        assert response_json[0]['username'] == username

    def test_get_user_by_username(self):
        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }

        # given - create user
        username = 'test'
        service = UserService(session=self.session)
        entity = service.create_user(
            username=username,
            password_clear='test'
        )

        # when
        response = self.test_api.get(
            url="/user/by_username",
            headers=headers,
            params={'username': username}
        )
        response_json = response.json()

        # then
        assert response_json['id'] == str(entity.id)
        assert response_json['username'] == username

    def test_get_not_existing_user_by_username(self):
        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }
        username = 'test'

        # when
        response = self.test_api.get(
            url="/user/by_username",
            headers=headers,
            params={'username': username}
        )
        response_json = response.json()

        # then
        assert "Not found user with username" in response_json['detail']

    def test_user_login(self):
        # given - create user
        username = 'test'
        password = 'test'
        service = UserService(session=self.session)
        service.create_user(
            username=username,
            password_clear=password
        )

        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }
        payload = dict(
            username=username,
            password=password
        )

        # when
        response = self.test_api.post(
            url="/user/login",
            headers=headers,
            json=payload

        )
        response_json = response.json()

        # then
        assert response_json['token'] != ''

    def test_user_login_invalid(self):
        # given - create user
        username = 'test'
        password = 'test'
        service = UserService(session=self.session)
        service.create_user(
            username=username,
            password_clear=password
        )

        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }
        payload = dict(
            username=username,
            password='invalid_pass'
        )

        # when
        response = self.test_api.post(
            url="/user/login",
            headers=headers,
            json=payload

        )
        response_json = response.json()

        # then
        assert "invalid username" in response_json['detail'].lower()

    def test_user_login_but_user_not_exists(self):
        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }
        payload = dict(
            username='test',
            password='test'
        )

        # when
        response = self.test_api.post(
            url="/user/login",
            headers=headers,
            json=payload

        )
        response_json = response.json()

        # then
        assert "invalid username" in response_json['detail'].lower()

    def test_user_create(self):
        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }

        username = 'test'
        payload = dict(
            username=username,
            password='test',
        )

        # when
        response = self.test_api.post(
            url="/user/create",
            headers=headers,
            json=payload

        )
        response_json = response.json()

        # then
        assert response_json['id']
        assert response_json['username'] == username

    def test_user_create_twice(self):
        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }

        username = 'test'
        payload = dict(
            username=username,
            password='test',
        )

        # when
        response = self.test_api.post(
            url="/user/create",
            headers=headers,
            json=payload

        )
        response_json = response.json()

        # then
        assert response_json['id']
        assert response_json['username'] == username

        # when
        response = self.test_api.post(
            url="/user/create",
            headers=headers,
            json=payload

        )

        # then
        assert response.status_code == 400

    def test_user_update(self):
        # given - create user
        username = 'test'
        password = 'test'

        service = UserService(session=self.session)
        entity = service.create_user(
            username=username,
            password_clear=password
        )
        user_id = str(entity.id)

        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }
        payload = dict(
            user_id=user_id,
            password=password
        )

        # when
        response = self.test_api.post(
            url="/user/update",
            headers=headers,
            json=payload

        )
        response_json = response.json()

        # then
        assert response_json['id'] == user_id
        assert response_json['username'] == username

    def test_user_update_when_user_not_exists(self):
        # given - create user
        password = 'test'
        user_id = str(uuid.uuid4())

        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }
        payload = dict(
            user_id=user_id,
            password=password,
        )

        # when
        response = self.test_api.post(
            url="/user/update",
            headers=headers,
            json=payload

        )
        response_json = response.json()

        # then
        assert response.status_code == 400
        assert 'user update error' in response_json['detail'].lower()

    def test_user_delete(self):
        # given - create users
        service = UserService(session=self.session)
        entity1 = service.create_user(
            username='test',
            password_clear='test'
        )
        entity2 = service.create_user(
            username='test2',
            password_clear='test'
        )
        user_to_del_id = str(entity1.id)

        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }
        payload = dict(
            user_id=user_to_del_id,
        )

        # when
        response = self.test_api.delete(
            url="/user/delete",
            headers=headers,
            params=payload
        )
        response_json = response.json()
        user_entities = service.find_all()

        # then
        assert len(user_entities) == 1
        assert user_entities[0].username == entity2.username
        assert response_json['id'] == str(entity1.id)

    def test_user_delete_when_user_not_exists(self):
        # given - create users
        service = UserService(session=self.session)
        user_to_del_id = str(uuid.uuid4())

        # given
        API_AUTH_TOKEN = os.environ['API_AUTH_MASTER_TOKEN']
        headers = {
            "X-API-KEY": API_AUTH_TOKEN,
            'Accept': 'application/json'
        }
        payload = dict(
            user_id=user_to_del_id,
        )

        # when
        response = self.test_api.delete(
            url="/user/delete",
            headers=headers,
            params=payload
        )
        response_json = response.json()
        user_entities = service.find_all()

        # then
        assert len(user_entities) == 0
        assert response.status_code == 400
        assert 'user delete error' in response_json['detail'].lower()