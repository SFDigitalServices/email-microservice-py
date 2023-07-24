""" Test fixtures """
import pytest
from falcon import testing
import service.microservice
from service.resources.db import create_session

CLIENT_HEADERS = {
    "ACCESS_KEY": "1234567"
}

@pytest.fixture()
def client():
    """ client fixture """
    return testing.TestClient(app=service.microservice.start_service(), headers=CLIENT_HEADERS)

@pytest.fixture
def mock_env_access_key(monkeypatch):
    """ mock environment access key """
    monkeypatch.setenv("ACCESS_KEY", CLIENT_HEADERS["ACCESS_KEY"])
    monkeypatch.setenv("SENDGRID_API_KEY", "abc123")

@pytest.fixture
def mock_env_no_access_key(monkeypatch):
    """ mock environment with no access key """
    monkeypatch.delenv("ACCESS_KEY", raising=False)

@pytest.fixture()
def db_session():
    """ set up """
    # pylint: disable=no-member
    session = create_session()
    database_session = session()
    yield database_session
    database_session.close()
