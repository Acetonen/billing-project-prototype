import pytest

from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def set_test_settings(settings):
    settings.DEBUG = True


@pytest.fixture
def ac():
    return APIClient()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
