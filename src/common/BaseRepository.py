import abc
from typing import Any


class NotFoundEntityError(Exception):
    ...


class BaseRepository(abc.ABC):
    def __init__(self, session):
        self.session = session

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