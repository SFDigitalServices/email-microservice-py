"""db module"""
import os
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as postgres
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

db_engine = sa.create_engine(os.environ.get('DATABASE_URL'), echo=True, pool_pre_ping=True) # pylint: disable=invalid-name
BASE = declarative_base()

def create_session(expire_on_commit=True):
    """creates database session"""
    return sessionmaker(bind=db_engine, expire_on_commit=expire_on_commit)

class HistoryModel(BASE):
    # pylint: disable=too-few-public-methods
    """Map History object to db"""

    __tablename__ = 'history'

    id = sa.Column(sa.Integer, primary_key=True)
    request = sa.Column(postgres.JSONB, nullable=False)
    email_content = sa.Column(postgres.JSONB)
    result = sa.Column(sa.TEXT)
    date_created = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    processed_timestamp = sa.Column(sa.DateTime(timezone=True))
