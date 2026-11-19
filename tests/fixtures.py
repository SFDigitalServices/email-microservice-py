""" Test fixtures """
import pytest
from falcon import testing

CLIENT_HEADERS = {
    "ACCESS_KEY": "1234567"
}

@pytest.fixture()
def client(require_database):
    """ client fixture - requires DATABASE_URL to be configured """
    # pylint: disable=unused-argument,import-outside-toplevel
    # Import here (after require_database validates) to avoid importing
    # service.microservice if DATABASE_URL is not set
    import service.microservice
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
def db_session(require_database):
    """ set up - requires DATABASE_URL to be configured """
    # pylint: disable=unused-argument,import-outside-toplevel,no-member
    # Import here (after require_database validates) to avoid importing
    # service.resources.db if DATABASE_URL is not set
    from service.resources.db import create_session
    session = create_session()
    database_session = session()
    yield database_session
    database_session.close()
