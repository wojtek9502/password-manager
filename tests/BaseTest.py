from unittest import TestCase

import pytest
from sqlalchemy import inspect, text

from src import engine


class BaseTest(TestCase):
    @pytest.fixture(scope="function", autouse=True)
    def setup_test(self):
        self.cleanup_db()

    @staticmethod
    def cleanup_db():
        db_inspect = inspect(engine)
        tables = sorted(db_inspect.get_table_names())
        tables.remove("alembic_version")

        connection = engine.connect()
        transaction = connection.begin()
        try:
            for table in reversed(tables):
                sql = text(f"TRUNCATE TABLE {table} CASCADE")
                connection.execute(statement=sql)
            transaction.commit()
        except Exception:
            transaction.rollback()
            raise
        finally:
            connection.close()

