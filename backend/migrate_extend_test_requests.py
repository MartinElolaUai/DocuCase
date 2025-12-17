"""
Extend test_requests table with richer fields for type, environment,
authentication and detailed plans for frontend/API tests.

Run once:
    python migrate_extend_test_requests.py
"""

from sqlalchemy import text

from app.database import engine


def migrate() -> None:
    """Add new columns to test_requests if they don't exist."""
    print("Starting migration for test_requests extra fields...")

    with engine.connect() as conn:
        try:
            result = conn.execute(
                text(
                    """
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'test_requests'
                    """
                )
            )
            existing = {row[0] for row in result}

            # type
            if "type" not in existing:
                conn.execute(
                    text(
                        "ALTER TABLE test_requests "
                        "ADD type NVARCHAR(20) NOT NULL DEFAULT 'FRONT'"
                    )
                )
                print("  Added column: type")

            # environment
            if "environment" not in existing:
                conn.execute(
                    text(
                        "ALTER TABLE test_requests "
                        "ADD environment NVARCHAR(50) NULL"
                    )
                )
                print("  Added column: environment")

            # has_auth
            if "has_auth" not in existing:
                conn.execute(
                    text(
                        "ALTER TABLE test_requests "
                        "ADD has_auth BIT NOT NULL DEFAULT 0"
                    )
                )
                print("  Added column: has_auth")

            # auth_type
            if "auth_type" not in existing:
                conn.execute(
                    text(
                        "ALTER TABLE test_requests "
                        "ADD auth_type NVARCHAR(100) NULL"
                    )
                )
                print("  Added column: auth_type")

            # auth_users (JSON as NVARCHAR(MAX))
            if "auth_users" not in existing:
                conn.execute(
                    text(
                        "ALTER TABLE test_requests "
                        "ADD auth_users NVARCHAR(MAX) NULL"
                    )
                )
                print("  Added column: auth_users")

            # front_plan (JSON as NVARCHAR(MAX))
            if "front_plan" not in existing:
                conn.execute(
                    text(
                        "ALTER TABLE test_requests "
                        "ADD front_plan NVARCHAR(MAX) NULL"
                    )
                )
                print("  Added column: front_plan")

            # api_plan (JSON as NVARCHAR(MAX))
            if "api_plan" not in existing:
                conn.execute(
                    text(
                        "ALTER TABLE test_requests "
                        "ADD api_plan NVARCHAR(MAX) NULL"
                    )
                )
                print("  Added column: api_plan")

            conn.commit()
            print("Migration for test_requests completed successfully.")

        except Exception as exc:  # noqa: BLE001
            print(f"Migration failed: {exc}")
            conn.rollback()
            raise


if __name__ == "__main__":
    migrate()


