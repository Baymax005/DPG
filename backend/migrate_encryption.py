"""
Migrate Existing Wallets to New Encryption System
Converts wallets encrypted with old Fernet-only system to new salt-based system
"""
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from database import SessionLocal
from models import Wallet
from crypto_manager import get_crypto_manager

load_dotenv()


def migrate_wallet_encryption():
    """
    Migrate all wallets from old encryption to new salt-based encryption.
    
    This is a one-time migration script.
    """
    print("=" * 70)
    print("🔄 Wallet Encryption Migration Tool")
    print("=" * 70)
    print()
    
    # Check if new master key exists
    if not os.getenv("WALLET_MASTER_KEY"):
        print("❌ WALLET_MASTER_KEY not found in .env!")
        print()
        print("Run this first:")
        print("  python backend/generate_master_key.py")
        print()
        return False
    
    # Get old encryption key (if exists)
    old_key = os.getenv("WALLET_ENCRYPTION_KEY")
    if not old_key:
        print("⚠️  WALLET_ENCRYPTION_KEY not found in .env")
        print()
        print("This is needed to decrypt existing wallets.")
        print()
        response = input("Do you have existing encrypted wallets to migrate? (yes/no): ").lower().strip()
        
        if response == 'yes':
            print()
            print("Please add your old WALLET_ENCRYPTION_KEY to .env file")
            print("Then run this script again.")
            print()
            return False
        else:
            print()
            print("✅ No migration needed - you can start fresh with new system!")
            print()
            return True
    
    print(f"📝 Found old encryption key: {old_key[:20]}...")
    print()
    
    # Initialize old cipher
    try:
        old_cipher = Fernet(old_key.encode())
        print("✅ Old encryption key validated")
    except Exception as e:
        print(f"❌ Invalid old encryption key: {e}")
        return False
    
    # Initialize new crypto manager
    try:
        crypto_manager = get_crypto_manager()
        print("✅ New crypto manager initialized")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize new crypto manager: {e}")
        return False
    
    # Get database session
    db: Session = SessionLocal()
    
    try:
        # Find all wallets with encrypted private keys
        wallets = db.query(Wallet).filter(
            Wallet.private_key_encrypted.isnot(None)
        ).all()
        
        if not wallets:
            print("ℹ️  No encrypted wallets found in database")
            print("✅ Migration not needed")
            print()
            return True
        
        print(f"🔍 Found {len(wallets)} wallet(s) to migrate")
        print()
        
        # Confirm migration
        print("⚠️  This will re-encrypt all wallets with the new system.")
        response = input("Continue? (yes/no): ").lower().strip()
        
        if response != 'yes':
            print("\n✅ Migration cancelled")
            return False
        
        print()
        print("🔄 Starting migration...")
        print()
        
        success_count = 0
        failed_count = 0
        
        for wallet in wallets:
            try:
                # Decrypt with old key
                decrypted_key = old_cipher.decrypt(wallet.private_key_encrypted.encode()).decode()
                
                # Re-encrypt with new system
                new_encrypted = crypto_manager.encrypt_private_key(decrypted_key)
                
                # Update wallet
                wallet.private_key_encrypted = new_encrypted
                
                success_count += 1
                print(f"✅ Migrated wallet {wallet.id} ({wallet.currency_code})")
                
            except Exception as e:
                failed_count += 1
                print(f"❌ Failed to migrate wallet {wallet.id}: {e}")
        
        # Commit changes
        if success_count > 0:
            db.commit()
            print()
            print(f"✅ Successfully migrated {success_count} wallet(s)")
        
        if failed_count > 0:
            print(f"⚠️  Failed to migrate {failed_count} wallet(s)")
        
        print()
        
        if success_count == len(wallets):
            print("🎉 Migration complete!")
            print()
            print("📋 Next steps:")
            print("1. Remove old WALLET_ENCRYPTION_KEY from .env (keep backup)")
            print("2. Restart backend server")
            print("3. Test wallet operations")
            print()
            return True
        else:
            print("⚠️  Migration incomplete - some wallets failed")
            return False
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    success = migrate_wallet_encryption()
    sys.exit(0 if success else 1)
