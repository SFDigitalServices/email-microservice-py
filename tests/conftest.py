"""Pytest configuration and shared fixtures"""

import os

# DATABASE_URL must be set and point to a configured, migrated PostgreSQL database
if not os.environ.get("DATABASE_URL"):
    raise RuntimeError(
        "DATABASE_URL environment variable is required for tests. "
        "Please configure a PostgreSQL test database and run migrations:\n"
        "  export DATABASE_URL=postgresql://user:password@localhost/test_db\n"
        "  alembic upgrade head"
    )

# Ensure SENDGRID_API_KEY is set for imports
if not os.environ.get("SENDGRID_API_KEY"):
    os.environ["SENDGRID_API_KEY"] = "test_key"
