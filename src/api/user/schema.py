import uuid

from pydantic import BaseModel


class LoginRequestSchema(BaseModel):
    username: str
    password: str


class UserCreateRequestSchema(BaseModel):
    username: str
    password: str


class UserUpdateRequestSchema(BaseModel):
    user_id: uuid.UUID
    password: str


class LoginResponseSchema(BaseModel):
    token: str


class UserUuidResponseSchema(BaseModel):
    id: uuid.UUID


class UserResponseSchema(BaseModel):
    id: uuid.UUID
    username: str
