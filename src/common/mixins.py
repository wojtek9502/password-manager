import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declared_attr


class InsertedOnMixin:
    @declared_attr
    def inserted_on(self):
        return Column(
            DateTime(timezone=True),
            default=datetime.datetime.now(),
            nullable=False
        )


class UpdatedOnMixin:
    @declared_attr
    def updated_on(self):
        return Column(
            DateTime(timezone=True),
            default=datetime.datetime.now,
            onupdate=datetime.datetime.now,
            nullable=False
        )

