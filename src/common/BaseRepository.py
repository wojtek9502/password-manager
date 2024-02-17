import abc
from typing import Any

from sqlalchemy.orm import sessionmaker

from src import engine


class NotFoundEntityError(Exception):
    ...

Session = sessionmaker(bind=engine, expire_on_commit=False, autocommit=False, autoflush=False)


class BaseRepository(abc.ABC):
    def __init__(self):
        self.session = Session()

    def __del__(self):
        if self.session.is_active:
            self.session.close()

    @abc.abstractmethod
    def model_class(self):
        ...

    def get_by_id(self, id_: Any):
        return self.session.get(self.model_class(), id_)

    def commit(self):
        self.session.commit()

    def save(self, entity):
        self.session.add(entity)

    def query(self):
        return self.session.query(self.model_class())