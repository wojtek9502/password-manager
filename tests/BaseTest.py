from unittest import TestCase

import pytest


class BaseTest(TestCase):
    @pytest.fixture(scope="function", autouse=True)
    def setup_test(self):
        ...

