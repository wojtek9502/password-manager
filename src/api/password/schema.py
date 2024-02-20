import uuid
from typing import List, Optional

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
    password_id: uuid.UUID
    name: str
    login: str
    password_encrypted: str
    client_side_algo: str
    client_side_iterations: int
    user_id: uuid.UUID
    note: Optional[str] = ''

    urls: Optional[List[PasswordUrlResponseSchema]] = []
    history: Optional[List[PasswordHistoryResponseSchema]] = []
    groups: Optional[List[PasswordGroupResponseSchema]] = []


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
    groups_ids: List[uuid.UUID]


class PasswordCreateResponseSchema(BaseModel):
    password_id: uuid.UUID
    name: str
    login: str
    user_id: uuid.UUID
    note: Optional[str] = ''
    urls: Optional[List[str]] = []
    groups_ids: Optional[List[uuid.UUID]] = []


class PasswordUpdateRequestSchema(BaseModel):
    password_id: uuid.UUID
    name: str
    login: str
    password_encrypted: str
    client_side_algo: str
    client_side_iterations: int
    note: str
    urls: List[str]
    groups_ids: List[uuid.UUID]


class PasswordUpdateResponseSchema(BaseModel):
    password_id: uuid.UUID
    name: str
    login: str
    user_id: uuid.UUID
    note: Optional[str] = ''
    urls: Optional[List[str]] = []
    groups_ids: Optional[List[uuid.UUID]] = []


class PasswordDeleteResponseSchema(BaseModel):
    password_id: uuid.UUID
