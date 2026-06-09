"""
Tests for migration 4dd3f9030cea — polymorphic source refactor.

Before: Single Source table with all fields flat (Splitter, FieldName, SheetName,
        HeaderRow, DatabaseId, SQLText, LLMId, LLMPromptTemplate, LLMSystemPrompt etc.)
After:  Base Source table with discriminator column, and subtype tables
        SourceCSV, SourceExcel, SourceDatabase, SourceLLM containing type-specific fields.
"""

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from alembic import command

START_REVISION = "63915fea6ce7"
TARGET_REVISION = "4dd3f9030cea"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def alembic_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture
def alembic_config(alembic_engine):
    cfg = Config("alembic.ini", config_args={"DB_PATH": ""})
    cfg.set_main_option("sqlalchemy.url", str(alembic_engine.url))
    cfg.attributes["connection"] = alembic_engine.connect()
    return cfg


@pytest.fixture
def migrator(alembic_config, alembic_engine):
    class Migrator:
        def __init__(self, config, engine):
            self.config = config
            self.engine = engine

        def upgrade(self, revision: str = "head"):
            command.upgrade(self.config, revision)

        def sql(self, query: str, params: dict | None = None):
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                conn.commit()
                try:
                    return result.mappings().all()
                except Exception:
                    return []

        def scalar(self, query: str, params: dict | None = None):
            with self.engine.connect() as conn:
                return conn.execute(text(query), params or {}).scalar_one()

    return Migrator(alembic_config, alembic_engine)


@pytest.fixture
def at_start_revision(migrator):
    """Bring schema to the revision before the target and seed a Workflow."""
    migrator.upgrade(START_REVISION)
    migrator.sql("INSERT INTO Workflow (Id, Name) VALUES (1, 'Test Workflow')")
    return migrator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _source_type_id(migrator, name: str) -> int:
    return migrator.scalar("SELECT Id FROM SourceType WHERE Name = :n", {"n": name})


def _insert_llm_provider(migrator, name: str) -> int:
    """Insert an LLMProvider — only valid after TARGET_REVISION."""
    migrator.sql(
        "INSERT INTO LLMProvider (CommonName, LangChainName) VALUES (:n, :ln)",
        {"n": name, "ln": name},
    )
    return migrator.scalar("SELECT Id FROM LLMProvider WHERE CommonName = :n", {"n": name})


def _insert_llm(migrator, provider_id: int, model_name: str) -> int:
    """Insert an LLM — only valid after TARGET_REVISION."""
    migrator.sql(
        "INSERT INTO LLM (ProviderId, ModelName) VALUES (:pid, :mn)",
        {"pid": provider_id, "mn": model_name},
    )
    return migrator.scalar(
        "SELECT Id FROM LLM WHERE ProviderId = :pid AND ModelName = :mn",
        {"pid": provider_id, "mn": model_name},
    )


def _insert_database_meta(migrator, name: str, connection_string: str) -> int:
    migrator.sql(
        "INSERT INTO DatabaseMetaSource (Name, ConnectionString) VALUES (:n, :cs)",
        {"n": name, "cs": connection_string},
    )
    return migrator.scalar("SELECT Id FROM DatabaseMetaSource WHERE Name = :n", {"n": name})


def _insert_csv_source(migrator, splitter: int = 1, field_name: str | None = None) -> int:
    type_id = _source_type_id(migrator, "CSV")
    migrator.sql(
        "INSERT INTO Source (WorkflowId, TypeId, Step, Splitter, FieldName) VALUES (1, :tid, 1, :sp, :fn)",
        {"tid": type_id, "sp": splitter, "fn": field_name},
    )
    return migrator.scalar("SELECT MAX(Id) FROM Source")


def _insert_excel_source(
    migrator,
    splitter: int = 1,
    field_name: str | None = None,
    sheet_name: str | None = None,
    header_row: int | None = None,
) -> int:
    type_id = _source_type_id(migrator, "Excel")
    migrator.sql(
        "INSERT INTO Source (WorkflowId, TypeId, Step, Splitter, FieldName, SheetName, HeaderRow) "
        "VALUES (1, :tid, 1, :sp, :fn, :sn, :hr)",
        {"tid": type_id, "sp": splitter, "fn": field_name, "sn": sheet_name, "hr": header_row},
    )
    return migrator.scalar("SELECT MAX(Id) FROM Source")


def _insert_database_source(
    migrator,
    database_id: int,
    sql_text: str | None = None,
    splitter: int = 1,
    field_name: str | None = None,
) -> int:
    type_id = _source_type_id(migrator, "Database")
    migrator.sql(
        "INSERT INTO Source (WorkflowId, TypeId, Step, DatabaseId, SQLText, Splitter, FieldName) "
        "VALUES (1, :tid, 1, :did, :sql, :sp, :fn)",
        {"tid": type_id, "did": database_id, "sql": sql_text, "sp": splitter, "fn": field_name},
    )
    return migrator.scalar("SELECT MAX(Id) FROM Source")


# def _insert_llm_source(
#     migrator,
#     llm_id: int,
#     prompt_template: str | None = None,
#     system_prompt: str | None = None,
# ) -> int:
#     type_id = _source_type_id(migrator, "LLM")
#     migrator.sql(
#         "INSERT INTO Source (WorkflowId, TypeId, Step, LLMId, LLMPromptTemplate, LLMSystemPrompt) "
#         "VALUES (1, :tid, 1, :lid, :pt, :sp)",
#         {"tid": type_id, "lid": llm_id, "pt": prompt_template, "sp": system_prompt},
#     )
#     return migrator.scalar("SELECT MAX(Id) FROM Source")


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------


class TestSchemaAfterMigration:
    def test_subtype_tables_created(self, at_start_revision):
        m = at_start_revision
        m.upgrade(TARGET_REVISION)
        tables = {row["name"] for row in m.sql("SELECT name FROM sqlite_master WHERE type='table'")}
        for expected in ("SourceCSV", "SourceExcel", "SourceDatabase", "SourceLLM"):
            assert expected in tables, f"Expected table '{expected}' to exist"

    def test_discriminator_column_added_to_source(self, at_start_revision):
        m = at_start_revision
        m.upgrade(TARGET_REVISION)
        columns = {row["name"] for row in m.sql("PRAGMA table_info(Source)")}
        assert "discriminator" in columns

    def test_old_columns_removed_from_source(self, at_start_revision):
        m = at_start_revision
        m.upgrade(TARGET_REVISION)
        columns = {row["name"] for row in m.sql("PRAGMA table_info(Source)")}
        for old_col in (
            "Splitter",
            "FieldName",
            "SheetName",
            "HeaderRow",
            "Orientation",
            "DatabaseId",
            "SQLText",
            "KeyField",
            "ValueField",
            "LLMId",
            "LLMPromptTemplate",
            "LLMSystemPrompt",
        ):
            assert old_col not in columns, f"Column '{old_col}' should have been removed from Source"


# ---------------------------------------------------------------------------
# CSV source migration
# ---------------------------------------------------------------------------


class TestCSVSourceMigration:
    def test_discriminator_set(self, at_start_revision):
        m = at_start_revision
        src_id = _insert_csv_source(m, splitter=1)
        m.upgrade(TARGET_REVISION)
        row = m.sql("SELECT discriminator FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["discriminator"] == "csv"

    def test_splitter_row_migrated(self, at_start_revision):
        m = at_start_revision
        src_id = _insert_csv_source(m, splitter=1)
        m.upgrade(TARGET_REVISION)
        row = m.sql("SELECT IsSplitter, FieldName FROM SourceCSV WHERE Id = :id", {"id": src_id})[0]
        assert row["IsSplitter"] == 1
        assert row["FieldName"] is None

    def test_field_row_migrated(self, at_start_revision):
        m = at_start_revision
        src_id = _insert_csv_source(m, splitter=0, field_name="line_items")
        m.upgrade(TARGET_REVISION)
        row = m.sql("SELECT IsSplitter, FieldName FROM SourceCSV WHERE Id = :id", {"id": src_id})[0]
        assert row["IsSplitter"] == 0
        assert row["FieldName"] == "line_items"

    def test_row_exists_in_subtype_table(self, at_start_revision):
        m = at_start_revision
        src_id = _insert_csv_source(m)
        m.upgrade(TARGET_REVISION)
        count = m.scalar("SELECT COUNT(*) FROM SourceCSV WHERE Id = :id", {"id": src_id})
        assert count == 1

    def test_csv_not_in_other_subtype_tables(self, at_start_revision):
        m = at_start_revision
        src_id = _insert_csv_source(m)
        m.upgrade(TARGET_REVISION)
        for table in ("SourceExcel", "SourceDatabase", "SourceLLM"):
            count = m.scalar(f"SELECT COUNT(*) FROM {table} WHERE Id = :id", {"id": src_id})
            assert count == 0, f"CSV source should not appear in {table}"


# ---------------------------------------------------------------------------
# Excel source migration
# ---------------------------------------------------------------------------


class TestExcelSourceMigration:
    def test_discriminator_set(self, at_start_revision):
        m = at_start_revision
        src_id = _insert_excel_source(m)
        m.upgrade(TARGET_REVISION)
        row = m.sql("SELECT discriminator FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["discriminator"] == "excel"

    def test_excel_fields_migrated(self, at_start_revision):
        m = at_start_revision
        src_id = _insert_excel_source(m, sheet_name="Invoices", header_row=1, splitter=1)
        m.upgrade(TARGET_REVISION)
        row = m.sql(
            "SELECT SheetName, HeaderRow, IsSplitter, FieldName FROM SourceExcel WHERE Id = :id",
            {"id": src_id},
        )[0]
        assert row["SheetName"] == "Invoices"
        assert row["HeaderRow"] == 1
        assert row["IsSplitter"] == 1
        assert row["FieldName"] is None

    def test_field_mode_migrated(self, at_start_revision):
        m = at_start_revision
        src_id = _insert_excel_source(m, splitter=0, field_name="items", sheet_name="Items")
        m.upgrade(TARGET_REVISION)
        row = m.sql(
            "SELECT IsSplitter, FieldName FROM SourceExcel WHERE Id = :id",
            {"id": src_id},
        )[0]
        assert row["IsSplitter"] == 0
        assert row["FieldName"] == "items"

    def test_excel_not_in_other_subtype_tables(self, at_start_revision):
        m = at_start_revision
        src_id = _insert_excel_source(m)
        m.upgrade(TARGET_REVISION)
        for table in ("SourceCSV", "SourceDatabase", "SourceLLM"):
            count = m.scalar(f"SELECT COUNT(*) FROM {table} WHERE Id = :id", {"id": src_id})
            assert count == 0, f"Excel source should not appear in {table}"


# ---------------------------------------------------------------------------
# Database source migration
# ---------------------------------------------------------------------------


class TestDatabaseSourceMigration:
    def test_discriminator_set(self, at_start_revision):
        m = at_start_revision
        db_id = _insert_database_meta(m, "TestDB", "sqlite:///test.db")
        src_id = _insert_database_source(m, database_id=db_id)
        m.upgrade(TARGET_REVISION)
        row = m.sql("SELECT discriminator FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["discriminator"] == "database"

    def test_database_fields_migrated(self, at_start_revision):
        m = at_start_revision
        db_id = _insert_database_meta(m, "TestDB", "sqlite:///test.db")
        src_id = _insert_database_source(m, database_id=db_id, sql_text="SELECT * FROM invoices", splitter=1)
        m.upgrade(TARGET_REVISION)
        row = m.sql(
            "SELECT DatabaseId, SQLText, IsSplitter, FieldName FROM SourceDatabase WHERE Id = :id",
            {"id": src_id},
        )[0]
        assert row["DatabaseId"] == db_id
        assert row["SQLText"] == "SELECT * FROM invoices"
        assert row["IsSplitter"] == 1
        assert row["FieldName"] is None

    def test_field_mode_migrated(self, at_start_revision):
        m = at_start_revision
        db_id = _insert_database_meta(m, "TestDB2", "sqlite:///test2.db")
        src_id = _insert_database_source(m, database_id=db_id, splitter=0, field_name="summary")
        m.upgrade(TARGET_REVISION)
        row = m.sql(
            "SELECT IsSplitter, FieldName FROM SourceDatabase WHERE Id = :id",
            {"id": src_id},
        )[0]
        assert row["IsSplitter"] == 0
        assert row["FieldName"] == "summary"

    def test_database_not_in_other_subtype_tables(self, at_start_revision):
        m = at_start_revision
        db_id = _insert_database_meta(m, "TestDB3", "sqlite:///test3.db")
        src_id = _insert_database_source(m, database_id=db_id)
        m.upgrade(TARGET_REVISION)
        for table in ("SourceCSV", "SourceExcel", "SourceLLM"):
            count = m.scalar(f"SELECT COUNT(*) FROM {table} WHERE Id = :id", {"id": src_id})
            assert count == 0, f"Database source should not appear in {table}"


# ---------------------------------------------------------------------------
# LLM source migration
# ---------------------------------------------------------------------------


class TestLLMSourceMigration:
    # LLMProvider and LLM tables don't exist at START_REVISION — they are created
    # by this migration. SQLite does not enforce FK constraints by default, so we
    # insert a raw LLMId integer of 1 and verify it is carried across correctly.

    def test_discriminator_set(self, at_start_revision):
        m = at_start_revision
        src_id = _insert_llm_source(m, llm_id=1)
        m.upgrade(TARGET_REVISION)
        row = m.sql("SELECT discriminator FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["discriminator"] == "llm"

    def test_llm_fields_migrated(self, at_start_revision):
        m = at_start_revision
        src_id = _insert_llm_source(
            m,
            llm_id=1,
            prompt_template="Summarise: {text}",
            system_prompt="You are a helpful assistant.",
        )
        m.upgrade(TARGET_REVISION)
        row = m.sql(
            "SELECT LLMId, LLMPromptTemplate, LLMSystemPrompt FROM SourceLLM WHERE Id = :id",
            {"id": src_id},
        )[0]
        assert row["LLMId"] == 1
        assert row["LLMPromptTemplate"] == "Summarise: {text}"
        assert row["LLMSystemPrompt"] == "You are a helpful assistant."

    def test_llm_source_not_in_other_subtype_tables(self, at_start_revision):
        m = at_start_revision
        src_id = _insert_llm_source(m, llm_id=1)
        m.upgrade(TARGET_REVISION)
        for table in ("SourceCSV", "SourceExcel", "SourceDatabase"):
            count = m.scalar(f"SELECT COUNT(*) FROM {table} WHERE Id = :id", {"id": src_id})
            assert count == 0, f"LLM source should not appear in {table}"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_no_sources_succeeds(self, at_start_revision):
        """Migration should complete cleanly with no Source rows."""
        m = at_start_revision
        m.upgrade(TARGET_REVISION)
        count = m.scalar("SELECT COUNT(*) FROM Source")
        assert count == 0

    def test_mixed_sources_all_migrated(self, at_start_revision):
        """Insert one of each type and verify all land in the correct subtype table."""
        m = at_start_revision
        db_id = _insert_database_meta(m, "MainDB", "sqlite:///main.db")

        csv_id = _insert_csv_source(m, splitter=1)
        excel_id = _insert_excel_source(m, sheet_name="Sheet1", splitter=1)
        database_id = _insert_database_source(m, database_id=db_id)
        llm_src_id = _insert_llm_source(m, llm_id=1)  # raw int — LLM table doesn't exist yet

        m.upgrade(TARGET_REVISION)

        assert m.scalar("SELECT COUNT(*) FROM SourceCSV WHERE Id = :id", {"id": csv_id}) == 1
        assert m.scalar("SELECT COUNT(*) FROM SourceExcel WHERE Id = :id", {"id": excel_id}) == 1
        assert m.scalar("SELECT COUNT(*) FROM SourceDatabase WHERE Id = :id", {"id": database_id}) == 1
        assert m.scalar("SELECT COUNT(*) FROM SourceLLM WHERE Id = :id", {"id": llm_src_id}) == 1

    def test_base_shared_fields_preserved(self, at_start_revision):
        """Name and Step on the base Source table should be untouched by the migration."""
        m = at_start_revision
        type_id = _source_type_id(m, "CSV")
        m.sql(
            "INSERT INTO Source (WorkflowId, TypeId, Step, Name, Splitter) VALUES (1, :tid, 3, 'my_source', 1)",
            {"tid": type_id},
        )
        src_id = m.scalar("SELECT MAX(Id) FROM Source")
        m.upgrade(TARGET_REVISION)
        row = m.sql("SELECT Name, Step FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["Name"] == "my_source"
        assert row["Step"] == 3


def _ensure_llm_source_type(migrator) -> int:
    """Seed LLM SourceType if not present — it does not exist at START_REVISION."""
    existing = migrator.sql("SELECT Id FROM SourceType WHERE Name = 'LLM'")
    if existing:
        return existing[0]["Id"]
    migrator.sql("INSERT INTO SourceType (Name, IsSlow, IsFile, IsMulti) VALUES ('LLM', 0, 0, 0)")
    return migrator.scalar("SELECT Id FROM SourceType WHERE Name = 'LLM'")

def _insert_llm_source(
    migrator,
    llm_id: int = 1,
    prompt_template: str | None = None,
    system_prompt: str | None = None,
    field_name: str = "llm_output",
) -> int:
    # type_id = _ensure_llm_source_type(migrator)
    type_id = _source_type_id(migrator, "LLM")
    migrator.sql(
        "INSERT INTO Source (WorkflowId, TypeId, Step, Splitter, LLMId, LLMPromptTemplate, LLMSystemPrompt, FieldName) "
        "VALUES (1, :tid, 1, 1, :lid, :pt, :sp, :fn)",
        {"tid": type_id, "lid": llm_id, "pt": prompt_template, "sp": system_prompt, "fn": field_name},
    )
    return migrator.scalar("SELECT MAX(Id) FROM Source")
