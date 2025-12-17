"""
Migration script to add availability_url column to applications table.
Run this once to update the database schema.
"""
from sqlalchemy import text

from app.database import engine


def migrate() -> None:
    """Add availability_url column to applications table if it doesn't exist."""
    print("Starting migration for availability_url...")

    with engine.connect() as conn:
        try:
            # Check existing columns
            result = conn.execute(
                text(
                    """
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'applications'
                      AND COLUMN_NAME = 'availability_url'
                    """
                )
            )
            existing = [row[0] for row in result]

            if "availability_url" not in existing:
                print("  Adding availability_url column...")
                conn.execute(
                    text(
                        "ALTER TABLE applications "
                        "ADD availability_url NVARCHAR(MAX) NULL"
                    )
                )
                conn.commit()
                print("  availability_url column added")
            else:
                print("  availability_url column already exists")

            print("\nMigration completed successfully!")

        except Exception as exc:  # noqa: BLE001
            print(f"\nMigration failed: {exc}")
            conn.rollback()
            raise


if __name__ == "__main__":
    migrate()


