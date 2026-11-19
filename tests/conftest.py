"""Pytest configuration and shared fixtures"""

import os
import pytest

# Ensure SENDGRID_API_KEY is set for imports
if not os.environ.get("SENDGRID_API_KEY"):
    os.environ["SENDGRID_API_KEY"] = "test_key"


@pytest.fixture
def require_database():
    """Fixture that requires DATABASE_URL to be configured.

    Use this fixture in tests that need database access.
    Fails early with clear instructions if PostgreSQL is not configured.
    """
    if not os.environ.get("DATABASE_URL"):
        raise RuntimeError(
            "DATABASE_URL environment variable is required for database tests. "
            "Please configure a PostgreSQL test database and run migrations:\n"
            "  export DATABASE_URL=postgresql://user:password@localhost/test_db\n"
            "  alembic upgrade head"
        )
