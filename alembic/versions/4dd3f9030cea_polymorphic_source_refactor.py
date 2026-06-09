"""
polymorphic_source_refactor

Revision ID: 4dd3f9030cea
Revises: 63915fea6ce7
Create Date: 2026-06-04 17:41:54.757528

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4dd3f9030cea"
down_revision: Union[str, Sequence[str], None] = "63915fea6ce7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Create new subtype tables
    op.create_table(
        "SourceCSV",
        sa.Column("Id", sa.Integer(), nullable=False),
        sa.Column("IsSplitter", sa.Boolean(), nullable=False),
        sa.Column("FieldName", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["Id"], ["Source.Id"]),
        sa.PrimaryKeyConstraint("Id"),
    )
    op.create_table(
        "SourceExcel",
        sa.Column("Id", sa.Integer(), nullable=False),
        sa.Column("SheetName", sa.Text(), nullable=True),
        sa.Column("HeaderRow", sa.Integer(), nullable=True),
        sa.Column("IsSplitter", sa.Boolean(), nullable=False),
        sa.Column("FieldName", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["Id"], ["Source.Id"]),
        sa.PrimaryKeyConstraint("Id"),
    )
    op.create_table(
        "SourceDatabase",
        sa.Column("Id", sa.Integer(), nullable=False),
        sa.Column("DatabaseId", sa.Integer(), nullable=False),
        sa.Column("SQLText", sa.Text(), nullable=True),
        sa.Column("IsSplitter", sa.Boolean(), nullable=False),
        sa.Column("FieldName", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["DatabaseId"], ["DatabaseMetaSource.Id"]),
        sa.ForeignKeyConstraint(["Id"], ["Source.Id"]),
        sa.PrimaryKeyConstraint("Id"),
    )
    op.create_table(
        "SourceLLM",
        sa.Column("Id", sa.Integer(), nullable=False),
        sa.Column("LLMId", sa.Integer(), nullable=False),
        sa.Column("LLMPromptTemplate", sa.Text(), nullable=True),
        sa.Column("LLMSystemPrompt", sa.Text(), nullable=True),
        sa.Column("FieldName", sa.Text(), nullable=False, default="llm_output"),
        sa.ForeignKeyConstraint(["Id"], ["Source.Id"]),
        sa.ForeignKeyConstraint(["LLMId"], ["LLM.Id"]),
        sa.PrimaryKeyConstraint("Id"),
    )

    # Step 2: Add discriminator column (nullable until populated)
    op.add_column("Source", sa.Column("discriminator", sa.String(length=50), nullable=True))

    # Step 3: Populate discriminator and subtype tables
    conn = op.get_bind()

    # Use SourceType names rather than hardcoded IDs for safety
    conn.execute(
        sa.text("UPDATE Source SET discriminator = 'csv' WHERE TypeId = (SELECT Id FROM SourceType WHERE Name = 'CSV')")
    )
    conn.execute(
        sa.text(
            "UPDATE Source SET discriminator = 'excel' WHERE TypeId = (SELECT Id FROM SourceType WHERE Name = 'Excel')"
        )
    )
    conn.execute(
        sa.text(
            "UPDATE Source SET discriminator = 'database' "
            "WHERE TypeId = (SELECT Id FROM SourceType WHERE Name = 'Database')"
        )
    )
    conn.execute(
        sa.text("UPDATE Source SET discriminator = 'llm' WHERE TypeId = (SELECT Id FROM SourceType WHERE Name = 'LLM')")
    )

    # Verify nothing was left unmapped — fail loudly if so
    unmapped = conn.execute(sa.text("SELECT COUNT(*) FROM Source WHERE discriminator IS NULL")).scalar()
    if unmapped:
        raise ValueError(
            f"Migration failed: {unmapped} Source row(s) have no discriminator mapping. "
            "Check for unexpected SourceType values."
        )

    conn.execute(
        sa.text("""
        INSERT INTO SourceCSV (Id, IsSplitter, FieldName)
        SELECT Id, COALESCE(Splitter, 1), FieldName
        FROM Source
        WHERE discriminator = 'csv'
    """)
    )
    conn.execute(
        sa.text("""
        INSERT INTO SourceExcel (Id, SheetName, HeaderRow, IsSplitter, FieldName)
        SELECT Id, SheetName, HeaderRow, COALESCE(Splitter, 1), FieldName
        FROM Source
        WHERE discriminator = 'excel'
    """)
    )
    conn.execute(
        sa.text("""
        INSERT INTO SourceDatabase (Id, DatabaseId, SQLText, IsSplitter, FieldName)
        SELECT Id, DatabaseId, SQLText, COALESCE(Splitter, 1), FieldName
        FROM Source
        WHERE discriminator = 'database'
    """)
    )
    conn.execute(
        sa.text("""
        INSERT INTO SourceLLM (Id, LLMId, LLMPromptTemplate, LLMSystemPrompt, FieldName)
        SELECT Id, LLMId, LLMPromptTemplate, LLMSystemPrompt, COALESCE(FieldName, 'llm_output')
        FROM Source
        WHERE discriminator = 'llm'
    """)
    )

    # Step 4: Drop old columns using batch mode — required for SQLite to handle
    # FK-referencing columns cleanly by reconstructing the table.
    with op.batch_alter_table("Source") as batch_op:
        batch_op.drop_column("Splitter")
        batch_op.drop_column("FieldName")
        batch_op.drop_column("SheetName")
        batch_op.drop_column("HeaderRow")
        batch_op.drop_column("Orientation")
        batch_op.drop_column("DatabaseId")
        batch_op.drop_column("SQLText")
        batch_op.drop_column("KeyField")
        batch_op.drop_column("ValueField")
        batch_op.drop_column("LLMId")
        batch_op.drop_column("LLMPromptTemplate")
        batch_op.drop_column("LLMSystemPrompt")

        # Made the discriminator not nullable
        batch_op.alter_column("discriminator", nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("Source") as batch_op:
        batch_op.add_column(sa.Column("LLMId", sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column("LLMPromptTemplate", sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column("LLMSystemPrompt", sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column("KeyField", sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column("ValueField", sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column("SQLText", sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column("DatabaseId", sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column("Orientation", sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column("HeaderRow", sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column("SheetName", sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column("FieldName", sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column("Splitter", sa.INTEGER(), nullable=True))

    # Restore data from subtype tables using SQLite-compatible subquery syntax
    conn = op.get_bind()

    conn.execute(
        sa.text("""
        UPDATE Source SET
            Splitter = (SELECT IsSplitter FROM SourceCSV WHERE SourceCSV.Id = Source.Id),
            FieldName = (SELECT FieldName FROM SourceCSV WHERE SourceCSV.Id = Source.Id)
        WHERE discriminator = 'csv'
    """)
    )
    conn.execute(
        sa.text("""
        UPDATE Source SET
            SheetName = (SELECT SheetName FROM SourceExcel WHERE SourceExcel.Id = Source.Id),
            HeaderRow = (SELECT HeaderRow FROM SourceExcel WHERE SourceExcel.Id = Source.Id),
            Splitter = (SELECT IsSplitter FROM SourceExcel WHERE SourceExcel.Id = Source.Id),
            FieldName = (SELECT FieldName FROM SourceExcel WHERE SourceExcel.Id = Source.Id)
        WHERE discriminator = 'excel'
    """)
    )
    conn.execute(
        sa.text("""
        UPDATE Source SET
            DatabaseId = (SELECT DatabaseId FROM SourceDatabase WHERE SourceDatabase.Id = Source.Id),
            SQLText = (SELECT SQLText FROM SourceDatabase WHERE SourceDatabase.Id = Source.Id),
            Splitter = (SELECT IsSplitter FROM SourceDatabase WHERE SourceDatabase.Id = Source.Id),
            FieldName = (SELECT FieldName FROM SourceDatabase WHERE SourceDatabase.Id = Source.Id)
        WHERE discriminator = 'database'
    """)
    )
    conn.execute(
        sa.text("""
        UPDATE Source SET
            LLMId = (SELECT LLMId FROM SourceLLM WHERE SourceLLM.Id = Source.Id),
            LLMPromptTemplate = (SELECT LLMPromptTemplate FROM SourceLLM WHERE SourceLLM.Id = Source.Id),
            LLMSystemPrompt = (SELECT LLMSystemPrompt FROM SourceLLM WHERE SourceLLM.Id = Source.Id)
        WHERE discriminator = 'llm'
    """)
    )

    op.drop_column("Source", "discriminator")
    op.drop_table("SourceLLM")
    op.drop_table("SourceDatabase")
    op.drop_table("SourceExcel")
    op.drop_table("SourceCSV")
