
from sqlalchemy import Column, UUID, String, Integer, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship

from src.common.BaseModel import BaseModel
from src.common.mixins import InsertedOnMixin, UpdatedOnMixin
from src.group.models import GroupModel

MODULE_PREFIX = 'us_'


class UserModel(BaseModel, InsertedOnMixin, UpdatedOnMixin):
    __tablename__ = MODULE_PREFIX + 'user'
    __uuid_column_name__ = 'id'

    id = Column(UUID(as_uuid=True), primary_key=True)
    username = Column(String(512), unique=True, nullable=False)
    password_hash = Column(LargeBinary(8192), unique=False, nullable=False)
    salt = Column(LargeBinary(256), nullable=False)
    hash_algo = Column(String(10), nullable=False)
    iterations = Column(Integer(), nullable=False)
    password_crypto = Column(LargeBinary(8192), unique=False, nullable=False)

    groups = relationship('GroupModel', secondary=MODULE_PREFIX + 'user_group', back_populates='users')

class UserTokenModel(BaseModel, InsertedOnMixin):
    __tablename__ = MODULE_PREFIX + 'user_token'
    __uuid_column_name__ = 'id'

    id = Column(UUID(as_uuid=True), primary_key=True)
    token = Column(String(512), unique=True, nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(UserModel.id), nullable=True)


class UserGroupModel(BaseModel):
    __tablename__ = MODULE_PREFIX + 'user_group'

    group_id = Column(UUID(as_uuid=True), ForeignKey(GroupModel.id), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(UserModel.id), primary_key=True)
