"""
Migration script to add asset_id and bapp_id columns to applications table.
Run this once to update the database schema.
"""
from sqlalchemy import text
from app.database import engine

def migrate():
    """Add asset_id and bapp_id columns to applications table."""
    print("🔄 Starting migration...")
    
    with engine.connect() as conn:
        try:
            # Check if columns already exist
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'applications' 
                AND COLUMN_NAME IN ('asset_id', 'bapp_id')
            """))
            existing = [row[0] for row in result]
            
            if 'asset_id' not in existing:
                print("  ➕ Adding asset_id column...")
                conn.execute(text("ALTER TABLE applications ADD asset_id NVARCHAR(255) NULL"))
                conn.execute(text("CREATE INDEX ix_applications_asset_id ON applications(asset_id)"))
                conn.commit()
                print("  ✅ asset_id column added")
            else:
                print("  ℹ️  asset_id column already exists")
            
            if 'bapp_id' not in existing:
                print("  ➕ Adding bapp_id column...")
                conn.execute(text("ALTER TABLE applications ADD bapp_id NVARCHAR(255) NULL"))
                conn.execute(text("CREATE INDEX ix_applications_bapp_id ON applications(bapp_id)"))
                conn.commit()
                print("  ✅ bapp_id column added")
            else:
                print("  ℹ️  bapp_id column already exists")
            
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()

