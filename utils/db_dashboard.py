"""
DPG Database Dashboard - View all data
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

# Create database connection
engine = create_engine(DATABASE_URL)

def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def get_table_stats():
    """Get statistics for all tables"""
    with engine.connect() as conn:
        print_header("📊 DPG DATABASE OVERVIEW")
        
        # Users count
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"👥 Total Users:        {user_count}")
        
        # Wallets count
        result = conn.execute(text("SELECT COUNT(*) FROM wallets"))
        wallet_count = result.scalar()
        print(f"💰 Total Wallets:      {wallet_count}")
        
        # Transactions count
        result = conn.execute(text("SELECT COUNT(*) FROM transactions"))
        tx_count = result.scalar()
        print(f"💸 Total Transactions: {tx_count}")
        
        # Active users
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE is_active = true"))
        active_users = result.scalar()
        print(f"✅ Active Users:       {active_users}")
        
        # Verified users
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE is_verified = true"))
        verified_users = result.scalar()
        print(f"✉️  Verified Users:     {verified_users}")
        
        print_header("👥 USERS DETAIL")
        
        # Get all users
        result = conn.execute(text("""
            SELECT 
                email, 
                first_name, 
                last_name, 
                is_active, 
                is_verified, 
                kyc_status,
                created_at
            FROM users 
            ORDER BY created_at DESC
        """))
        
        users = result.fetchall()
        
        if not users:
            print("❌ No users found")
        else:
            for idx, user in enumerate(users, 1):
                print(f"\n{idx}. 📧 {user[0]}")
                print(f"   👤 Name: {user[1] or 'N/A'} {user[2] or 'N/A'}")
                print(f"   ✅ Active: {user[3]} | Verified: {user[4]} | KYC: {user[5]}")
                print(f"   📅 Joined: {user[6].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check for wallets
        if wallet_count > 0:
            print_header("💰 WALLETS DETAIL")
            result = conn.execute(text("""
                SELECT 
                    w.currency_code,
                    w.wallet_type,
                    w.balance,
                    u.email,
                    w.created_at
                FROM wallets w
                JOIN users u ON w.user_id = u.id
                ORDER BY w.created_at DESC
            """))
            
            wallets = result.fetchall()
            for idx, wallet in enumerate(wallets, 1):
                print(f"\n{idx}. {wallet[0]} ({wallet[1]})")
                print(f"   💵 Balance: {wallet[2]}")
                print(f"   👤 Owner: {wallet[3]}")
                print(f"   📅 Created: {wallet[4].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check for transactions
        if tx_count > 0:
            print_header("💸 TRANSACTIONS DETAIL")
            result = conn.execute(text("""
                SELECT 
                    t.type,
                    t.amount,
                    t.status,
                    u.email,
                    t.created_at
                FROM transactions t
                JOIN wallets w ON t.wallet_id = w.id
                JOIN users u ON w.user_id = u.id
                ORDER BY t.created_at DESC
                LIMIT 10
            """))
            
            txs = result.fetchall()
            for idx, tx in enumerate(txs, 1):
                print(f"\n{idx}. {tx[0]} - {tx[1]} ({tx[2]})")
                print(f"   👤 User: {tx[3]}")
                print(f"   📅 Date: {tx[4].strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        get_table_stats()
        print("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"❌ Error: {e}")
