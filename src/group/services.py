import logging
import uuid
from typing import Optional, List

from src.common.BaseService import BaseService
from src.group.models import GroupModel
from src.group.repositories import GroupRepository
from src.password.repositories import PasswordGroupRepository

logger = logging.getLogger()


class GroupService(BaseService):
    def create(self, name: str, user_id: uuid.UUID) -> GroupModel:
        repo = GroupRepository(session=self.session)
        entity = repo.create(name=name, user_id=user_id)
        repo.save(entity)
        repo.commit()
        return entity

    def find_user_groups(self, user_id: uuid.UUID) -> List[GroupModel]:
        repo = GroupRepository(session=self.session)
        groups = repo.find_groups_by_user_id(user_id=user_id)
        return groups

    def update(self, group_id: uuid.UUID, new_name: str, user_id: uuid.UUID) -> Optional[GroupModel]:
        repo = GroupRepository(session=self.session)
        user_groups = self.find_user_groups(user_id)
        group_users = [group.users for group in user_groups]
        group_users_ids = [user.id for user in group_users]

        if user_id not in group_users_ids:
            raise Exception("This group not belong to user")

        entity = repo.update(
            entity_id=group_id,
            name=new_name
        )
        repo.save(entity)
        repo.commit()
        return entity

    def delete(self, group_id: uuid.UUID, user_id: uuid.UUID) -> uuid.UUID:
        group_repo = GroupRepository(session=self.session)
        group_entity = group_repo.find_by_id(group_id=group_id)
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
        return group_id

