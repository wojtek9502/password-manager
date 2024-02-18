from src.password.services import PasswordService
from src.password.types import PasswordDTO
from tests.BaseTest import BaseTest
from tests.password.utils import mock_client_side_password_encrypted, mock_password_group, mock_user


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
        password_entity = service.get(password_entity.id)

        password_entity_groups_names = [group.name for group in password_entity.groups]
        password_entity_urls = [url_entity.url for url_entity in password_entity.urls]

        # then
        assert password_entity_groups_names == [group_name]
        assert len(password_entity_urls) == len(password_urls)
        assert password_urls[0] in password_entity_urls
        assert password_urls[1] in password_entity_urls
