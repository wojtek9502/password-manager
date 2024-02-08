
from sqlalchemy import Column, UUID, String, Integer, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship

from src import UserModel
from src.common.BaseModel import BaseModel
from src.common.mixins import InsertedOnMixin, UpdatedOnMixin
from src.group.models import GroupModel

MODULE_PREFIX = 'pa_'


class PasswordModel(BaseModel, InsertedOnMixin, UpdatedOnMixin):
    __tablename__ = MODULE_PREFIX + 'password'
    __uuid_column_name__ = 'id'

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(4089), nullable=False)
    login = Column(String(2048), nullable=False)
    password_hash = Column(LargeBinary(8192), unique=False, nullable=False)
    salt = Column(LargeBinary(256), nullable=False)
    hash_algo = Column(String(30), nullable=False)
    iterations = Column(Integer(), nullable=False)
    note = Column(String(8192), unique=False, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey(UserModel.id), nullable=True)

    urls = relationship("PasswordUrlModel", backref="password")
    history = relationship("PasswordHistory", backref="password")
    groups = relationship('Group', secondary=MODULE_PREFIX + 'password_group', back_populates='passwords')


class PasswordUrlModel(BaseModel):
    __tablename__ = MODULE_PREFIX + 'password_url'
    __uuid_column_name__ = 'id'

    id = Column(UUID(as_uuid=True), primary_key=True)
    url = Column(String(4089), nullable=False)
    password_id = Column(UUID(as_uuid=True), ForeignKey(PasswordModel.id))


class PasswordHistory(BaseModel, InsertedOnMixin):
    __tablename__ = MODULE_PREFIX + 'password_history'
    __uuid_column_name__ = 'id'

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(4089), nullable=False)
    username = Column(String(2048), nullable=False)
    old_password_hash = Column(LargeBinary(8192), nullable=False)
    old_salt = Column(LargeBinary(256), nullable=False)
    hash_algo = Column(String(30), nullable=False)
    iterations = Column(Integer(), nullable=False)
    note = Column(String(8192), nullable=True)
    changed_bu_user_id = Column(UUID(as_uuid=True), ForeignKey(UserModel.id), nullable=True)
    password_id = Column(UUID(as_uuid=True), ForeignKey(PasswordModel.id), nullable=True)


class PasswordGroupModel(BaseModel):
    __tablename__ = MODULE_PREFIX + 'password_group'

    group_id = Column(UUID(as_uuid=True), ForeignKey(GroupModel.id), primary_key=True)
    password_id = Column(UUID(as_uuid=True), ForeignKey(PasswordModel.id), primary_key=True)

