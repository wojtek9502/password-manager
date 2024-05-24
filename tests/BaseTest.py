from unittest import TestCase

import pytest
from sqlalchemy import inspect, text

from src import engine
from src.common.db_session import Session


class BaseTest(TestCase):
    session = None

    def setUp(self):
        self.session = Session()

    def tearDown(self):
        if self.session.is_active:
            self.session.close()

    @pytest.fixture(scope="function", autouse=True)
    def setup_test(self):
        self.cleanup_db()

    @staticmethod
    def cleanup_db():
        db_inspect = inspect(engine)
        tables = sorted(db_inspect.get_table_names())
        if 'alembic_version' in tables:
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

