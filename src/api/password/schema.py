import uuid
from typing import List

from pydantic import BaseModel


class PasswordUrlResponseSchema(BaseModel):
    id: uuid.UUID
    url: str
    password_id: uuid.UUID


class PasswordGroupResponseSchema(BaseModel):
    group_id: uuid.UUID
    password_id: uuid.UUID
    name: str


class PasswordHistoryResponseSchema(BaseModel):
    id: uuid.UUID
    name: str
    login: str
    password_encrypted: str
    client_side_algo: str
    client_side_iterations: int
    note: str
    user_id: uuid.UUID
    password_id: uuid.UUID


class PasswordResponseSchema(BaseModel):
    id: uuid.UUID
    name: str
    login: str
    password_encrypted: str
    client_side_algo: str
    client_side_iterations: int
    note: str
    user_id: uuid.UUID

    urls: List[PasswordUrlResponseSchema]
    history: List[PasswordHistoryResponseSchema]
    groups: List[PasswordGroupResponseSchema]


class PasswordListResponseSchema(BaseModel):
    passwords: List[PasswordResponseSchema]


class PasswordCreateRequestSchema(BaseModel):
    name: str
    login: str
    password_encrypted: str
    client_side_algo: str
    client_side_iterations: int
    note: str
    urls: List[str]
    user_id: uuid.UUID
    groups_ids: List[uuid.UUID]


class PasswordCreateResponseSchema(BaseModel):
    name: str
    login: str
    note: str
    urls: List[str]
    user_id: uuid.UUID
    groups_ids: List[uuid.UUID]
