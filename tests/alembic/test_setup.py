import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

@pytest.fixture
def alembic_engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

@pytest.fixture
def alembic_config(alembic_engine):
    cfg = Config("alembic.ini", config_args={"DB_PATH": ""})
    cfg.set_main_option("sqlalchemy.url", str(alembic_engine.url))
    cfg.attributes["connection"] = alembic_engine.connect()
    return cfg

def test_debug_source_types(alembic_config, alembic_engine):
    command.upgrade(alembic_config, "63915fea6ce7")
    with alembic_engine.connect() as conn:
        rows = conn.execute(text("SELECT Id, Name FROM SourceType")).mappings().all()
        for row in rows:
            print(row)
