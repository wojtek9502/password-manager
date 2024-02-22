import logging
import os
import uuid
from typing import Optional, List

from src.common.BaseService import BaseService
from src.group.exceptions import GroupDeleteNotAllowedError
from src.group.models import GroupModel
from src.group.repositories import GroupRepository
from src.password.repositories import PasswordGroupRepository
from src.user.repositories import UserGroupRepository

logger = logging.getLogger()


class GroupService(BaseService):
    def create_group(self, name: str) -> GroupModel:
        repo = GroupRepository(session=self.session)
        entity = repo.create_group(name=name)
        repo.save(entity)
        repo.commit()
        return entity

    def create_group_with_user(self, name: str, user_id: uuid.UUID) -> GroupModel:
        repo = GroupRepository(session=self.session)
        entity = repo.create_group_with_user(name=name, user_id=user_id)
        repo.save(entity)
        repo.commit()
        return entity

    def find_user_groups(self, user_id: uuid.UUID) -> List[GroupModel]:
        repo = GroupRepository(session=self.session)
        groups = repo.find_groups_by_user_id(user_id=user_id)
        return groups

    def update(self, group_id: uuid.UUID, new_name: str, user_id: uuid.UUID) -> Optional[GroupModel]:
        group_repo = GroupRepository(session=self.session)
        group_entity = group_repo.find_by_id(group_id=group_id)
        group_users_ids = [user.id for user in group_entity.users]

        if user_id not in group_users_ids:
            raise Exception("This group not belong to user")

        entity = group_repo.update(
            entity_id=group_id,
            name=new_name
        )
        group_repo.save(entity)
        group_repo.commit()
        return entity

    def delete(self, group_id: uuid.UUID, user_id: uuid.UUID) -> uuid.UUID:
        group_repo = GroupRepository(session=self.session)
        group_user_repo = UserGroupRepository(session=self.session)
        group_entity = group_repo.find_by_id(group_id=group_id)
        if group_entity.name == os.environ['USER_DEFAULT_GROUP_NAME']:
            raise GroupDeleteNotAllowedError('Cannot delete user default group')

        group_users_ids = [user.id for user in group_entity.users]
        if user_id not in group_users_ids:
            raise Exception("This group not belong to user")

        # move passwords to default group
        user_default_group = group_repo.find_user_default_group(user_id=user_id)
        password_group_repo = PasswordGroupRepository(self.session)
        password_group_repo.move_passwords_from_group_to_group(
            src_group_id=group_id,
            dst_group_id=user_default_group.id
        )

        # delete users from many to many user-group db
        group_user_repo.delete_user_from_all_groups(user_id=user_id)

        # delete repo
        group_repo.delete_by_id(group_id=group_id)
        return group_id

