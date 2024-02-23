import os
import uuid

from src.api.group.schema import GroupCreateRequestSchema, GroupUpdateRequestSchema
from src.group.repositories import GroupRepository
from tests.api.ApiBaseTests import ApiBaseTest
from tests.test_utils.create_db_resources import create_test_user_and_get_token, create_group_with_user


class ApiGroupTests(ApiBaseTest):
    def test_list_groups(self):
        # given
        user_id, user_token = create_test_user_and_get_token(session=self.session)
        group_name1 = 'test'
        group_name2 = 'test'
        expected_group_num = 3  # three + default group created when user is created

        create_group_with_user(
            session=self.session,
            user_id=user_id,
            group_name=group_name1
        )
        create_group_with_user(
            session=self.session,
            user_id=user_id,
            group_name=group_name2
        )

        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }

        # when
        response = self.test_api.get(
            url="/group/list",
            headers=headers
        )
        response_json = response.json()
        group_names = [group_json['name'] for group_json in response_json]
        groups_all = GroupRepository(session=self.session).get_all()

        # then
        assert len(groups_all) == expected_group_num
        assert os.environ['USER_DEFAULT_GROUP_NAME'] in group_names
        assert group_name1 in group_names
        assert group_name2 in group_names

    def test_create_group(self):
        # given
        expected_group_num = 2  # one + default group created when user is created
        user_id, user_token = create_test_user_and_get_token(session=self.session)
        group_name1 = 'test'

        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }
        create_data = GroupCreateRequestSchema(
            name=group_name1
        )
        payload = create_data.model_dump()

        # when
        response = self.test_api.post(
            url="/group/create",
            headers=headers,
            json=payload
        )
        response_json = response.json()
        created_group_name = response_json['name']
        groups_all = GroupRepository(session=self.session).get_all()

        # then
        assert len(groups_all) == expected_group_num
        assert created_group_name == group_name1

    def test_update_group(self):
        # given
        expected_group_num = 2  # one + default group created when user is created
        user_id, user_token = create_test_user_and_get_token(session=self.session)
        old_group_name = 'test'
        new_group_name = 'test_new'

        group_entity = create_group_with_user(
            session=self.session,
            user_id=user_id,
            group_name='test'
        )

        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }
        update_data = GroupUpdateRequestSchema(
            group_id=group_entity.id,
            name=new_group_name
        )
        payload = update_data.model_dump()
        payload['group_id'] = str(payload['group_id'])

        # when
        response = self.test_api.post(
            url="/group/update",
            headers=headers,
            json=payload
        )
        response_json = response.json()
        updated_group_name = response_json['name']
        groups_all = GroupRepository(session=self.session).get_all()

        # then
        assert len(groups_all) == expected_group_num
        assert updated_group_name != old_group_name
        assert updated_group_name == new_group_name

    def test_delete_group(self):
        # given
        expected_group_num = 1  # default group is always created when user is created
        user_id, user_token = create_test_user_and_get_token(session=self.session)
        group_entity = create_group_with_user(
            session=self.session,
            user_id=user_id,
            group_name='test'
        )
        group_to_delete_id = str(group_entity.id)

        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }
        payload = dict(
            group_id=group_entity.id
        )

        # when
        response = self.test_api.delete(
            url="/group/delete",
            headers=headers,
            params=payload
        )
        response_json = response.json()
        deleted_group_id = response_json['group_id']
        groups_all = GroupRepository(session=self.session).get_all()

        # then
        assert len(groups_all) == expected_group_num
        assert deleted_group_id == group_to_delete_id

    def test_delete_default_group(self):
        # given
        # create user and default group for user
        user_id, user_token = create_test_user_and_get_token(session=self.session)

        user_default_group = GroupRepository(session=self.session).find_user_default_group(user_id=user_id)
        group_to_delete_id = str(user_default_group.id)

        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }
        payload = dict(
            group_id=group_to_delete_id
        )

        # when
        response = self.test_api.delete(
            url="/group/delete",
            headers=headers,
            params=payload
        )
        response_json = response.json()

        # then
        assert response.status_code == 400
        assert 'Cannot delete user default group' in response_json['detail']

    def test_delete_when_group_not_exists(self):
        # given
        user_id, user_token = create_test_user_and_get_token(session=self.session)

        random_uuid = uuid.uuid4()
        group_to_delete_id = str(random_uuid)

        headers = {
            "X-API-KEY": user_token,
            'Accept': 'application/json'
        }
        payload = dict(
            group_id=group_to_delete_id
        )

        # when
        response = self.test_api.delete(
            url="/group/delete",
            headers=headers,
            params=payload
        )
        response_json = response.json()

        # then
        assert response.status_code == 400
        assert 'Delete error' in response_json['detail']


