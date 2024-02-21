import dataclasses
import uuid
from typing import Optional


@dataclasses.dataclass
class GroupDTO:
    name: str
    id: Optional[uuid.UUID] = None
