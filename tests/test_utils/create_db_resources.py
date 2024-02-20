import uuid
from typing import Tuple

from sqlalchemy.orm import Session

from src import GroupModel
from src.group.services import GroupService
from src.user.services import UserService, UserTokenService


def create_group(session: Session, group_name: str = 'test') -> GroupModel:
    group_service = GroupService(session=session)
    group_entity = group_service.create(group_name)
    return group_entity


def create_test_user_and_get_token(session: Session, user: str = 'test',
                                   password_clear: str = 'test') -> Tuple[uuid.UUID, str]:
    user_service = UserService(session=session)
    user_token_service = UserTokenService(session=session)

    user_entity = user_service.create_user(username=user, password_clear=password_clear)
    user_login_token = user_service.login_user(username=user, password_clear=password_clear)

    user_token_service.create_token(
        token=user_login_token,
        user_id=user_entity.id
    )
    return user_entity.id, user_login_token
