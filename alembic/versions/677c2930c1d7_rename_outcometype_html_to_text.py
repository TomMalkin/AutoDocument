"""
Rename OutcomeType HTML to Text.

Revision ID: 677c2930c1d7
Revises: e3280edb70e5
Create Date: 2025-11-27 10:06:33.265232

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "677c2930c1d7"
down_revision: Union[str, Sequence[str], None] = "e3280edb70e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Update the OutcomeType name."""
    op.execute("""
        UPDATE "OutcomeType"
        SET "Name" = 'Text'
        WHERE "Name" = 'HTML';
    """)


def downgrade():
    """Reverse the change in case of downgrade."""
    op.execute("""
        UPDATE "OutcomeType"
        SET "Name" = 'HTML'
        WHERE "Name" = 'Text';
    """)
