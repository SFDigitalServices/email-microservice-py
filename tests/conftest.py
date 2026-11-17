"""Pytest configuration and shared fixtures"""

import os
import pytest

# Ensure SENDGRID_API_KEY is set for imports
if not os.environ.get("SENDGRID_API_KEY"):
    os.environ["SENDGRID_API_KEY"] = "test_key"


def pytest_configure(config):
    """Validate DATABASE_URL before collecting tests that need it.

    This runs before any test module imports, so we can catch missing
    DATABASE_URL and display clear instructions before the import of
    service.resources.db tries to create_engine().
    """
    # pylint: disable=unused-argument
    if not os.environ.get("DATABASE_URL"):
        raise RuntimeError(
            "DATABASE_URL environment variable is required for tests. "
            "Please configure a PostgreSQL test database and run migrations:\n"
            "  export DATABASE_URL=postgresql://user:password@localhost/test_db\n"
            "  alembic upgrade head"
        )


@pytest.fixture
def require_database():
    """Fixture that documents database dependency for individual tests.

    This fixture is used to mark tests that require database access.
    The actual validation happens in pytest_configure() before collection.
    """
