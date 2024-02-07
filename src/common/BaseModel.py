import uuid

from src.common.Database import Database


class BaseModel(Database):
    __abstract__ = True
    __uuid_column_name__: str = None  # Auto generate UUID

    def __init__(self, *args, **kwargs):
        if self.__uuid_column_name__:
            auto_value = uuid.uuid4()
            setattr(self, self.__uuid_column_name__, auto_value)
        super().__init__(*args, **kwargs)
