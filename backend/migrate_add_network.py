"""
Database Migration: Add network column to transactions table
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    """Add network column to transactions table"""
    print("=" * 70)
    print("🔧 Database Migration: Add network column")
    print("=" * 70)
    print()
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("📋 Checking if network column already exists...")
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='transactions' AND column_name='network';
        """)
        
        exists = cursor.fetchone()
        
        if exists:
            print("✅ Column 'network' already exists - nothing to do!")
            cursor.close()
            conn.close()
            return True
        
        print("➕ Adding 'network' column to transactions table...")
        
        # Add network column with default value 'sepolia'
        cursor.execute("""
            ALTER TABLE transactions 
            ADD COLUMN network VARCHAR DEFAULT 'sepolia';
        """)
        
        conn.commit()
        
        print("✅ Column added successfully!")
        print()
        print("📋 Updating existing transactions...")
        
        # Set network for existing transactions
        cursor.execute("""
            UPDATE transactions 
            SET network = 'sepolia' 
            WHERE network IS NULL;
        """)
        
        conn.commit()
        
        rows_updated = cursor.rowcount
        print(f"✅ Updated {rows_updated} existing transaction(s)")
        print()
        print("🎉 Migration completed successfully!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    success = migrate()
    
    if success:
        print()
        print("=" * 70)
        print("Next Steps:")
        print("1. ✅ Database migrated")
        print("2. 🔄 Restart backend: python backend/main.py")
        print("3. ✅ Transaction monitor will now work properly")
        print("=" * 70)
    else:
        print()
        print("⚠️  Migration failed. Check error above.")
    
    exit(0 if success else 1)
