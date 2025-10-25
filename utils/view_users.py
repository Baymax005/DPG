"""
View all registered users from the database
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

# Create database session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Get all users
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    print("="*80)
    print(f"📊 DPG REGISTERED USERS - Total: {len(users)}")
    print("="*80)
    
    if not users:
        print("❌ No users found in database")
    else:
        for idx, user in enumerate(users, 1):
            print(f"\n{'='*80}")
            print(f"User #{idx}")
            print(f"{'='*80}")
            print(f"🆔 ID:           {user.id}")
            print(f"📧 Email:        {user.email}")
            print(f"👤 Name:         {user.first_name or 'N/A'} {user.last_name or 'N/A'}")
            print(f"📱 Phone:        {user.phone or 'N/A'}")
            print(f"✅ Active:       {user.is_active}")
            print(f"✉️  Verified:     {user.is_verified}")
            print(f"🔐 KYC Status:   {user.kyc_status.value}")
            print(f"📅 Created:      {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if user.last_login:
                print(f"🕐 Last Login:   {user.last_login.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"🕐 Last Login:   Never")
            
            # Count wallets if relationship exists
            if hasattr(user, 'wallets') and user.wallets:
                print(f"💰 Wallets:      {len(user.wallets)}")
    
    print("\n" + "="*80)
    
finally:
    db.close()
