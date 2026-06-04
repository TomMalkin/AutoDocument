"""
Tests for migration 63915fea6ce7 — squash source types.

Before: SQL Record, SQL RecordSet, SQL RecordSet Transpose, CSVRecord, CSVTable,
        ExcelRecord, ExcelTable are separate SourceTypes.
After:  All collapsed into Database, CSV, Excel.
        - Single-record variants had Splitter=0 (NOT NULL column, defaulted to 0);
          migration sets them to 1.
        - Multi-record variants already had Splitter set (0 or 1); migration
          only updates TypeId and leaves their existing Splitter value untouched.
"""

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

START_REVISION = "677c2930c1d7"
TARGET_REVISION = "63915fea6ce7"

# Old type names that should be deleted by the migration
OLD_TYPE_NAMES = (
    "SQL Record",
    "SQL RecordSet",
    "SQL RecordSet Transpose",
    "CSVRecord",
    "CSVTable",
    "ExcelRecord",
    "ExcelTable",
    "SQL RecordScalar",
)

# New consolidated type names that must exist after migration
NEW_TYPE_NAMES = ("Database", "CSV", "Excel")


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
    """Bring schema up to the revision immediately before the target and seed old source types."""
    migrator.upgrade(START_REVISION)

    # Insert the full set of old SourceTypes that existed before this migration.
    # IsSlow/IsFile/IsMulti values match what would be in a real pre-migration DB.
    old_types = [
        # name,                      IsSlow, IsFile, IsMulti
        ("SQL Record",               0,      0,      0),
        ("SQL RecordSet",            0,      0,      1),
        ("SQL RecordSet Transpose",  0,      0,      0),
        ("SQL RecordScalar",         0,      0,      0),
        ("CSVRecord",                0,      1,      0),
        ("CSVTable",                 0,      1,      1),
        ("ExcelRecord",              0,      1,      0),
        ("ExcelTable",               0,      1,      1),
    ]
    for name, is_slow, is_file, is_multi in old_types:
        migrator.sql(
            "INSERT INTO SourceType (Name, IsSlow, IsFile, IsMulti) VALUES (:n, :sl, :fi, :mu)",
            {"n": name, "sl": is_slow, "fi": is_file, "mu": is_multi},
        )

    # Insert a Workflow to satisfy the FK on Source
    migrator.sql("INSERT INTO Workflow (Id, Name) VALUES (1, 'Test Workflow')")

    return migrator


def _source_type_id(migrator, name: str) -> int:
    return migrator.scalar("SELECT Id FROM SourceType WHERE Name = :n", {"n": name})


def _insert_source(migrator, type_name: str, splitter: int = 0) -> int:
    """Insert a Source row for the given SourceType name and return its Id.

    Splitter is NOT NULL in the schema, so single-record sources are inserted
    with splitter=0 (the default that would have been set before this migration
    concept existed). The migration sets them to 1. Multi-record sources should
    be inserted with their actual pre-migration value (0 or 1).
    """
    type_id = _source_type_id(migrator, type_name)
    migrator.sql(
        """
        INSERT INTO Source (WorkflowId, TypeId, Splitter, Step)
        VALUES (1, :tid, :sp, 1)
        """,
        {"tid": type_id, "sp": splitter},
    )
    return migrator.scalar("SELECT last_insert_rowid()")


# ---------------------------------------------------------------------------
# Schema tests — new types exist, old types are gone
# ---------------------------------------------------------------------------

class TestSchemaAfterMigration:
    def test_new_types_created(self, at_start_revision):
        m = at_start_revision
        m.upgrade(TARGET_REVISION)
        names = {row["Name"] for row in m.sql("SELECT Name FROM SourceType")}
        for expected in NEW_TYPE_NAMES:
            assert expected in names, f"Expected new SourceType '{expected}' to exist"

    def test_old_types_removed(self, at_start_revision):
        m = at_start_revision
        m.upgrade(TARGET_REVISION)
        names = {row["Name"] for row in m.sql("SELECT Name FROM SourceType")}
        for old in OLD_TYPE_NAMES:
            assert old not in names, f"Old SourceType '{old}' should have been deleted"

    def test_new_types_are_multi(self, at_start_revision):
        """All consolidated types should have IsMulti = 1."""
        m = at_start_revision
        m.upgrade(TARGET_REVISION)
        for name in NEW_TYPE_NAMES:
            row = m.sql("SELECT IsMulti FROM SourceType WHERE Name = :n", {"n": name})[0]
            assert row["IsMulti"] == 1, f"SourceType '{name}' should have IsMulti = 1"


# ---------------------------------------------------------------------------
# Database source type consolidation
# ---------------------------------------------------------------------------

class TestDatabaseSourceType:
    def test_sql_record_becomes_database_with_splitter(self, at_start_revision):
        """SQL Record (single) — Splitter was 0 pre-migration, migration sets it to 1."""
        m = at_start_revision
        src_id = _insert_source(m, "SQL Record", splitter=0)
        m.upgrade(TARGET_REVISION)

        db_type_id = _source_type_id(m, "Database")
        row = m.sql("SELECT TypeId, Splitter FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["TypeId"] == db_type_id
        assert row["Splitter"] == 1

    def test_sql_recordset_transpose_becomes_database_with_splitter(self, at_start_revision):
        """SQL RecordSet Transpose (single) — Splitter was 0 pre-migration, migration sets it to 1."""
        m = at_start_revision
        src_id = _insert_source(m, "SQL RecordSet Transpose", splitter=0)
        m.upgrade(TARGET_REVISION)

        db_type_id = _source_type_id(m, "Database")
        row = m.sql("SELECT TypeId, Splitter FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["TypeId"] == db_type_id
        assert row["Splitter"] == 1

    def test_sql_recordset_preserves_splitter_0(self, at_start_revision):
        """SQL RecordSet (multi) with Splitter=0 — TypeId updated, Splitter stays 0."""
        m = at_start_revision
        src_id = _insert_source(m, "SQL RecordSet", splitter=0)
        m.upgrade(TARGET_REVISION)

        db_type_id = _source_type_id(m, "Database")
        row = m.sql("SELECT TypeId, Splitter FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["TypeId"] == db_type_id
        assert row["Splitter"] == 0

    def test_sql_recordset_preserves_splitter_1(self, at_start_revision):
        """SQL RecordSet (multi) with Splitter=1 — TypeId updated, Splitter stays 1."""
        m = at_start_revision
        src_id = _insert_source(m, "SQL RecordSet", splitter=1)
        m.upgrade(TARGET_REVISION)

        db_type_id = _source_type_id(m, "Database")
        row = m.sql("SELECT TypeId, Splitter FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["TypeId"] == db_type_id
        assert row["Splitter"] == 1


# ---------------------------------------------------------------------------
# CSV source type consolidation
# ---------------------------------------------------------------------------

class TestCSVSourceType:
    def test_csv_record_becomes_csv_with_splitter(self, at_start_revision):
        """CSVRecord (single) — Splitter was 0 pre-migration, migration sets it to 1."""
        m = at_start_revision
        src_id = _insert_source(m, "CSVRecord", splitter=0)
        m.upgrade(TARGET_REVISION)

        csv_type_id = _source_type_id(m, "CSV")
        row = m.sql("SELECT TypeId, Splitter FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["TypeId"] == csv_type_id
        assert row["Splitter"] == 1

    def test_csv_table_preserves_splitter_0(self, at_start_revision):
        """CSVTable (multi) with Splitter=0 — TypeId updated, Splitter stays 0."""
        m = at_start_revision
        src_id = _insert_source(m, "CSVTable", splitter=0)
        m.upgrade(TARGET_REVISION)

        csv_type_id = _source_type_id(m, "CSV")
        row = m.sql("SELECT TypeId, Splitter FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["TypeId"] == csv_type_id
        assert row["Splitter"] == 0

    def test_csv_table_preserves_splitter_1(self, at_start_revision):
        """CSVTable (multi) with Splitter=1 — TypeId updated, Splitter stays 1."""
        m = at_start_revision
        src_id = _insert_source(m, "CSVTable", splitter=1)
        m.upgrade(TARGET_REVISION)

        csv_type_id = _source_type_id(m, "CSV")
        row = m.sql("SELECT TypeId, Splitter FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["TypeId"] == csv_type_id
        assert row["Splitter"] == 1


# ---------------------------------------------------------------------------
# Excel source type consolidation
# ---------------------------------------------------------------------------

class TestExcelSourceType:
    def test_excel_record_becomes_excel_with_splitter(self, at_start_revision):
        """ExcelRecord (single) — Splitter was 0 pre-migration, migration sets it to 1."""
        m = at_start_revision
        src_id = _insert_source(m, "ExcelRecord", splitter=0)
        m.upgrade(TARGET_REVISION)

        excel_type_id = _source_type_id(m, "Excel")
        row = m.sql("SELECT TypeId, Splitter FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["TypeId"] == excel_type_id
        assert row["Splitter"] == 1

    def test_excel_table_preserves_splitter_0(self, at_start_revision):
        """ExcelTable (multi) with Splitter=0 — TypeId updated, Splitter stays 0."""
        m = at_start_revision
        src_id = _insert_source(m, "ExcelTable", splitter=0)
        m.upgrade(TARGET_REVISION)

        excel_type_id = _source_type_id(m, "Excel")
        row = m.sql("SELECT TypeId, Splitter FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["TypeId"] == excel_type_id
        assert row["Splitter"] == 0

    def test_excel_table_preserves_splitter_1(self, at_start_revision):
        """ExcelTable (multi) with Splitter=1 — TypeId updated, Splitter stays 1."""
        m = at_start_revision
        src_id = _insert_source(m, "ExcelTable", splitter=1)
        m.upgrade(TARGET_REVISION)

        excel_type_id = _source_type_id(m, "Excel")
        row = m.sql("SELECT TypeId, Splitter FROM Source WHERE Id = :id", {"id": src_id})[0]
        assert row["TypeId"] == excel_type_id
        assert row["Splitter"] == 1


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_no_sources_succeeds(self, at_start_revision):
        """Migration should complete cleanly with no Source rows."""
        m = at_start_revision
        m.upgrade(TARGET_REVISION)  # should not raise
        count = m.scalar("SELECT COUNT(*) FROM Source")
        assert count == 0

    def test_migration_is_idempotent_for_new_types(self, at_start_revision):
        """
        If Database/CSV/Excel already exist before the migration runs
        (e.g. re-running on a partially migrated DB), the INSERT … WHERE NOT EXISTS
        guard should prevent duplicates.
        """
        m = at_start_revision
        # Pre-insert the new types to simulate a partial migration state
        for name, is_file in [("Database", 0), ("CSV", 1), ("Excel", 1)]:
            m.sql(
                "INSERT INTO SourceType (Name, IsSlow, IsFile, IsMulti) VALUES (:n, 0, :f, 1)",
                {"n": name, "f": is_file},
            )
        m.upgrade(TARGET_REVISION)

        for name in NEW_TYPE_NAMES:
            count = m.scalar(
                "SELECT COUNT(*) FROM SourceType WHERE Name = :n", {"n": name}
            )
            assert count == 1, f"Expected exactly one '{name}' SourceType, got {count}"

    def test_mixed_source_types_all_migrated(self, at_start_revision):
        """Insert sources of every old type with realistic pre-migration Splitter values."""
        m = at_start_revision

        # (old_type_name, pre_migration_splitter, expected_new_type, expected_splitter)
        cases = [
            ("SQL Record",              0, "Database", 1),  # single → forced to 1
            ("SQL RecordSet Transpose", 0, "Database", 1),  # single → forced to 1
            ("SQL RecordSet",           0, "Database", 0),  # multi, splitter preserved
            ("SQL RecordSet",           1, "Database", 1),  # multi, splitter preserved
            ("CSVRecord",               0, "CSV",      1),  # single → forced to 1
            ("CSVTable",                0, "CSV",      0),  # multi, splitter preserved
            ("CSVTable",                1, "CSV",      1),  # multi, splitter preserved
            ("ExcelRecord",             0, "Excel",    1),  # single → forced to 1
            ("ExcelTable",              0, "Excel",    0),  # multi, splitter preserved
            ("ExcelTable",              1, "Excel",    1),  # multi, splitter preserved
        ]

        src_ids = [
            (_insert_source(m, old_type, splitter=pre_splitter), new_type, exp_splitter)
            for old_type, pre_splitter, new_type, exp_splitter in cases
        ]

        m.upgrade(TARGET_REVISION)

        for src_id, new_type_name, exp_splitter in src_ids:
            new_type_id = _source_type_id(m, new_type_name)
            row = m.sql("SELECT TypeId, Splitter FROM Source WHERE Id = :id", {"id": src_id})[0]
            assert row["TypeId"] == new_type_id, (
                f"Source {src_id}: expected TypeId for '{new_type_name}', got {row['TypeId']}"
            )
            assert row["Splitter"] == exp_splitter, (
                f"Source {src_id}: expected Splitter={exp_splitter}, got {row['Splitter']}"
            )
