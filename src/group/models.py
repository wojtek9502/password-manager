
from sqlalchemy import Column, UUID, String
from sqlalchemy.orm import relationship

from src.common.BaseModel import BaseModel


MODULE_PREFIX = 'gr_'


class GroupModel(BaseModel):
    __tablename__ = MODULE_PREFIX + 'group'
    __uuid_column_name__ = 'id'

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(4089), unique=False, nullable=False)

    users = relationship('UserModel', secondary='us_user_group', back_populates='groups',)
    passwords = relationship('PasswordModel', secondary='pa_password_group', back_populates='groups')