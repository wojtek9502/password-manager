from src.group.repositories import GroupRepository
from src.password.repositories import PasswordUrlRepository, PasswordHistoryRepository, \
    PasswordRepository
from src.password.services import PasswordService
from src.password.types import PasswordDTO
from tests.BaseTest import BaseTest
from tests.password.utils import mock_client_side_password_encrypted, mock_password_group, mock_user, \
    mock_password_history


class PasswordServiceTests(BaseTest):
    def test_create_password(self):
        # given
        service = PasswordService(session=self.session)
        name = 'test password'
        login = 'test@test.pl'
        client_side_iterations = 600_000

        # password groups
        group_name = 'group1'
        group1_id = mock_password_group(db_session=self.session, group_name=group_name).id
        groups_ids = [group1_id]

        # password urls
        password_urls = ['https://website1.pl', 'https://website2.pl']

        # create user
        user_id = mock_user(db_session=self.session, username='test', password_clear='test').id

        # client side password
        client_side_password_encrypted = mock_client_side_password_encrypted()

        password_details: PasswordDTO = PasswordDTO(
            name=name,
            login=login,
            server_side_algo='Fernet',
            server_side_iterations=600_000,
            client_side_password_encrypted=client_side_password_encrypted,
            client_side_algo='Fernet',
            client_side_iterations=client_side_iterations,
            note='',
            urls=password_urls,
            groups_ids=groups_ids,
            user_id=user_id
        )

        # when
        password_entity = service.create(
            password_details=password_details
        )

        password_entity_groups_names = [group.name for group in password_entity.groups]
        password_entity_urls = [url_entity.url for url_entity in password_entity.urls]

        # then
        assert password_entity_groups_names == [group_name]
        assert len(password_entity_urls) == len(password_urls)
        assert password_urls[0] in password_entity_urls
        assert password_urls[1] in password_entity_urls

    def test_update_password(self):
        # given
        service = PasswordService(session=self.session)
        old_name = 'test password'
        old_login = 'test@test.pl'
        old_password_clear = 'password1'
        client_side_iterations = 600_000

        # password groups
        group_name = 'group1'
        group1_id = mock_password_group(db_session=self.session, group_name=group_name).id
        old_groups_ids = [group1_id]

        # password urls
        old_password_urls = ['https://website1.pl', 'https://website2.pl']

        # create user
        user_id = mock_user(db_session=self.session, username='test', password_clear='test').id

        # client side password
        old_client_side_password_encrypted = mock_client_side_password_encrypted(old_password_clear)

        password_details: PasswordDTO = PasswordDTO(
            name=old_name,
            login=old_login,
            server_side_algo='Fernet',
            server_side_iterations=600_000,
            client_side_password_encrypted=old_client_side_password_encrypted,
            client_side_algo='Fernet',
            client_side_iterations=client_side_iterations,
            note='',
            urls=old_password_urls,
            groups_ids=old_groups_ids,
            user_id=user_id
        )

        # when - create password
        old_password_entity = service.create(
            password_details=password_details
        )
        old_password_encrypted = old_password_entity.password_encrypted

        password_entity_groups_names = [group.name for group in old_password_entity.groups]
        password_entity_urls = [url_entity.url for url_entity in old_password_entity.urls]

        # then
        assert password_entity_groups_names == [group_name]
        assert len(password_entity_urls) == len(old_password_urls)
        assert old_password_urls[0] in password_entity_urls
        assert old_password_urls[1] in password_entity_urls

        # given - update password
        new_login = 'login2'
        new_name = 'name2'
        new_password_clear = 'password2'
        new_client_side_password_encrypted = mock_client_side_password_encrypted(new_password_clear)

        password_new_details: PasswordDTO = PasswordDTO(
            name=new_name,
            login=new_login,
            server_side_algo='Fernet',
            server_side_iterations=600_000,
            client_side_password_encrypted=new_client_side_password_encrypted,
            client_side_algo='Fernet',
            client_side_iterations=client_side_iterations,
            note='',
            urls=old_password_urls,
            groups_ids=old_groups_ids,
            user_id=user_id
        )

        # when - update password
        new_password_entity = service.update(
            entity_id=old_password_entity.id,
            password_new_details=password_new_details
        )

        # then - check is password updated, check password history entity
        assert new_password_entity.name == new_name
        assert new_password_entity.name != old_name
        assert new_password_entity.login == new_login
        assert new_password_entity.login != old_login
        assert new_password_entity.password_encrypted != old_password_encrypted

        assert len(new_password_entity.urls) == len(old_password_entity.urls)
        assert len(new_password_entity.groups) == len(old_password_entity.groups)

        assert len(new_password_entity.history) > 0
        assert new_password_entity.history[0].name != new_password_entity.name

    def test_delete_password(self):
        # given
        password_service = PasswordService(session=self.session)
        password_repo = PasswordRepository(session=self.session)
        password_url_repo = PasswordUrlRepository(session=self.session)
        group_repo = GroupRepository(session=self.session)
        password_history_repo = PasswordHistoryRepository(session=self.session)

        # given - password groups
        group_name = 'group1'
        group1_id = mock_password_group(db_session=self.session, group_name=group_name).id
        old_groups_ids = [group1_id]

        # given - password urls
        old_password_urls = ['https://website1.pl', 'https://website2.pl']

        # given - create user
        user_id = mock_user(db_session=self.session, username='test', password_clear='test').id

        # given - client side password
        client_site_password_clear = 'password1'
        old_client_side_password_encrypted = mock_client_side_password_encrypted(client_site_password_clear)

        password_details: PasswordDTO = PasswordDTO(
            name='test password',
            login='test@test.pl',
            server_side_algo='Fernet',
            server_side_iterations=600_000,
            client_side_password_encrypted=old_client_side_password_encrypted,
            client_side_algo='Fernet',
            client_side_iterations=600_000,
            note='',
            urls=old_password_urls,
            groups_ids=old_groups_ids,
            user_id=user_id
        )

        # when - create password, create password history
        password_entity = password_service.create(
            password_details=password_details
        )
        mock_password_history(
            db_session=self.session,
            password_id=password_entity.id,
            password_details=password_details
        )

        # when - collect entities
        user_passwords_entities = password_repo.find_all_by_user(user_id=user_id)
        password_urls_entities = password_url_repo.find_all_by_password_id(password_id=password_entity.id)
        password_history_entities = password_history_repo.find_all_by_password_id(password_id=password_entity.id)
        group_entity = group_repo.find_by_id(group_id=group1_id)

        # then - check password created
        assert len(user_passwords_entities) != 0
        assert len(password_urls_entities) != 0
        assert len(password_history_entities) != 0
        assert len(group_entity.passwords) != 0

        # when - delete password
        deleted_password_ids = password_service.delete(password_id=password_entity.id, user_id=user_id)

        # when - collect entities
        user_passwords_entities = password_repo.find_all_by_user(user_id=user_id)
        password_urls_entities = password_url_repo.find_all_by_password_id(password_id=deleted_password_ids)
        password_history_entities = password_history_repo.find_all_by_password_id(password_id=deleted_password_ids)
        group_entity = group_repo.find_by_id(group_id=group1_id)

        # then - check password deleted
        assert len(user_passwords_entities) == 0
        assert len(password_urls_entities) == 0
        assert len(password_history_entities) == 0
        assert len(group_entity.passwords) == 0
