import uuid

from pydantic import BaseModel


class GroupResponseSchema(BaseModel):
    group_id: uuid.UUID
    name: str


class GroupCreateRequestSchema(BaseModel):
    name: str


class GroupUpdateRequestSchema(BaseModel):
    group_id: uuid.UUID
    name: str


class GroupDeleteResponseSchema(BaseModel):
    group_id: uuid.UUID
