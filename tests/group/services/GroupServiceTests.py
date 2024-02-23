import pytest

from src.group.exceptions import GroupDeleteNotAllowedError, GroupUpdateNotAllowedError
from src.group.services import GroupService
from src.password.services import PasswordService
from tests.BaseTest import BaseTest
from tests.test_utils.create_db_resources import create_user, create_group_with_user, create_password


class GroupServiceTests(BaseTest):
    def test_create_group_without_users(self):
        # given
        service = GroupService(session=self.session)
        name = 'test group'

        # when
        entity = service.create_group(
            name=name
        )

        # then
        assert entity.name == name
        assert not len(entity.users)
        assert not len(entity.passwords)

    def test_create_group_with_user(self):
        # given
        service = GroupService(session=self.session)

        name = 'test group'
        user_id = create_user(db_session=self.session, username='test', password_clear='test').id

        # when
        entity = service.create_group_with_user(
            name=name,
            user_id=user_id
        )

        # then
        assert entity.name == name
        assert len(entity.users) == 1
        assert not len(entity.passwords)

    def test_get_password_groups(self):
        # given
        group_service = GroupService(session=self.session)

        name = 'test group'
        user_id = create_user(db_session=self.session, username='test', password_clear='test').id
        group_entity = group_service.create_group_with_user(
            name=name,
            user_id=user_id
        )

        # when
        password_entity = create_password(
            session=self.session,
            group_ids=[group_entity.id],
            user_id=user_id, name='password1', login='test1')
        password_id = password_entity.id
        password_groups = group_service.find_password_groups(password_id=password_id)

        # then
        assert password_groups[0].name == name
        assert len(password_groups) == 1

    def test_update_group(self):
        # given
        old_name = 'old_name'
        new_name = 'new_name'

        service = GroupService(session=self.session)
        user_id = create_user(db_session=self.session, username='test', password_clear='test').id
        group_entity = create_group_with_user(session=self.session, group_name=old_name, user_id=user_id)

        # when
        updated_group_entity = service.update(group_id=group_entity.id, new_name=new_name, user_id=user_id)

        # then
        assert updated_group_entity.name == new_name
        assert updated_group_entity.name != old_name

    def test_update_group_when_group_not_belongs_to_user(self):
        # given
        old_name = 'old_name'
        new_name = 'new_name'

        service = GroupService(session=self.session)
        user1_id = create_user(db_session=self.session, username='test1', password_clear='test').id
        user2_id = create_user(db_session=self.session, username='test2', password_clear='test').id
        user1_group_entity = create_group_with_user(session=self.session, group_name=old_name, user_id=user1_id)

        # when
        with pytest.raises(GroupUpdateNotAllowedError) as exc_info:
            service.update(group_id=user1_group_entity.id, new_name=new_name, user_id=user2_id)

        # then
        assert isinstance(exc_info.value, GroupUpdateNotAllowedError)

    def test_delete_group(self):
        # given
        group_name = 'new'
        service = GroupService(session=self.session)
        user_id = create_user(db_session=self.session, username='test', password_clear='test').id
        group_entity = create_group_with_user(session=self.session, group_name=group_name, user_id=user_id)
        group_to_delete_id = group_entity.id

        # when
        deleted_group_id = service.delete(group_id=group_to_delete_id, user_id=user_id)
        user_groups = service.find_user_groups(user_id=user_id)
        user_groups_names = [group.name for group in user_groups]

        # then
        assert deleted_group_id == group_to_delete_id
        assert group_name not in user_groups_names

    def test_delete_group_not_belongs_to_user(self):
        # given
        service = GroupService(session=self.session)
        user1_id = create_user(db_session=self.session, username='test', password_clear='test').id
        user2_id = create_user(db_session=self.session, username='test2', password_clear='test2').id
        group_entity = create_group_with_user(session=self.session, group_name='group', user_id=user1_id)
        group_to_delete_id = group_entity.id

        # when
        with pytest.raises(GroupDeleteNotAllowedError) as exc_info:
            service.delete(group_id=group_to_delete_id, user_id=user2_id)

        # then
        assert isinstance(exc_info.value, GroupDeleteNotAllowedError)

