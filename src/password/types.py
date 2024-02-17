import dataclasses
import uuid
from typing import List


@dataclasses.dataclass
class PasswordHistoryDTO:
    name: str
    login: str
    password: str
    note: str
    password_id: uuid.UUID


@dataclasses.dataclass
class PasswordDTO:
    name: str
    login: str
    server_side_algo: str
    server_side_iterations: int
    client_side_password_encrypted: bytes
    client_side_algo: str
    client_side_iterations: int
    note: str
    urls: List[str]
    user_id: uuid.UUID
    groups_ids: List[uuid.UUID]
