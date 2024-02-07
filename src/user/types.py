import dataclasses


@dataclasses.dataclass
class UserJwtTokenPayload:
    username: str
