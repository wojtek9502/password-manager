import dataclasses
import uuid
from typing import List, Optional

@dataclasses.dataclass
class PasswordUrlDTO:
    name: str
    login: str
    client_side_password_encrypted: bytes
    client_side_algo: str
    client_side_iterations: int
    note: str
    password_id: uuid.UUID
    user_id: uuid.UUID
    id: Optional[uuid.UUID] = None


@dataclasses.dataclass
class PasswordHistoryDTO:
    name: str
    login: str
    client_side_password_encrypted: bytes
    client_side_algo: str
    client_side_iterations: int
    note: str
    password_id: uuid.UUID
    user_id: uuid.UUID
    id: Optional[uuid.UUID] = None


@dataclasses.dataclass
class PasswordDTO:
    name: str
    login: str
    password_encrypted: bytes
    client_side_algo: str
    client_side_iterations: int
    note: str
    user_id: uuid.UUID
    id: Optional[uuid.UUID] = None
    urls: List[str] = dataclasses.field(default_factory=list)
    history: List[PasswordHistoryDTO] = dataclasses.field(default_factory=list)
    groups_ids: List[uuid.UUID] = dataclasses.field(default_factory=list)
    server_side_algo: Optional[str] = 'fernet'
    server_side_iterations: Optional[int] = 600_000




