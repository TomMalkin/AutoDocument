"""
squash source types.

Multi and Single record types are being squashed into one type, where
a single type is now just a multi record splitter that happens to have
a single record.

Revision ID: 63915fea6ce7
Revises: 677c2930c1d7
Create Date: 2026-06-02 14:25:29.894025

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "63915fea6ce7"
down_revision: Union[str, Sequence[str], None] = "677c2930c1d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Squash types.

    Steps are:
        1) Ensure new types exist
        2) update current sources to the new type Ids
        3) Check all references to old types are gone
        4) remove old types
    """
    conn = op.get_bind()

    new_types = [
        ("Database", 0),
        ("CSV", 1),
        ("Excel", 1),
    ]

    # 1) Ensure new types exist
    for name, is_file in new_types:
        conn.execute(
            sa.text("""
                INSERT INTO SourceType (Name, IsSlow, IsFile, IsMulti)
                SELECT :name, 0, :is_file, 1
                WHERE NOT EXISTS (
                    SELECT 1 FROM SourceType WHERE Name = :name
                )
            """),
            {"name": name, "is_file": is_file},
        )

    # 2) update current sources to the new type Ids

    # Database
    database_type_id = conn.execute(sa.text("SELECT Id FROM SourceType WHERE Name = 'Database'")).scalar_one()
    conn.execute(
        sa.text("""
            UPDATE Source
            SET TypeId = :new_type_id, Splitter = 1
            WHERE TypeId IN (
                SELECT Id FROM SourceType
                WHERE Name IN ('SQL Record', 'SQL RecordSet Transpose')
            )
        """),
        {"new_type_id": database_type_id},
    )
    conn.execute(
        sa.text("""
            UPDATE Source
            SET TypeId = :new_type_id
            WHERE TypeId IN (
                SELECT Id FROM SourceType
                WHERE Name = 'SQL RecordSet'
            )
        """),
        {"new_type_id": database_type_id},
    )

    # Excel
    excel_type_id = conn.execute(sa.text("SELECT Id FROM SourceType WHERE Name = 'Excel'")).scalar_one()
    conn.execute(
        sa.text("""
            UPDATE Source
            SET TypeId = :new_type_id, Splitter = 1
            WHERE TypeId IN (
                SELECT Id FROM SourceType
                WHERE Name = 'ExcelRecord'
            )
        """),
        {"new_type_id": excel_type_id},
    )
    conn.execute(
        sa.text("""
            UPDATE Source
            SET TypeId = :new_type_id
            WHERE TypeId IN (
                SELECT Id FROM SourceType
                WHERE Name = 'ExcelTable'
            )
        """),
        {"new_type_id": excel_type_id},
    )

    # CSV
    csv_type_id = conn.execute(sa.text("SELECT Id FROM SourceType WHERE Name = 'CSV'")).scalar_one()
    conn.execute(
        sa.text("""
            UPDATE Source
            SET TypeId = :new_type_id, Splitter = 1
            WHERE TypeId IN (
                SELECT Id FROM SourceType
                WHERE Name = 'CSVRecord'
            )
        """),
        {"new_type_id": csv_type_id},
    )
    conn.execute(
        sa.text("""
            UPDATE Source
            SET TypeId = :new_type_id
            WHERE TypeId IN (
                SELECT Id FROM SourceType
                WHERE Name = 'CSVTable'
            )
        """),
        {"new_type_id": csv_type_id},
    )

    # 4) remove old types:
    conn.execute(
        sa.text("""
            delete from SourceType
            where Name in ('SQL Record', 'SQL RecordSet', 'SQL RecordSet Transpose', 'CSVRecord', 'CSVTable', 'ExcelRecord', 'ExcelTable', 'SQL RecordScalar')
        """)
    )

def downgrade() -> None:
    """Downgrade schema."""
    pass
