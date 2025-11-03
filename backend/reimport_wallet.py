"""
Re-import Wallet with New Encryption
This script re-encrypts your wallet with the new enterprise encryption system
"""
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from getpass import getpass

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from database import SessionLocal
from models import Wallet
from crypto_manager import encrypt_private_key

def reimport_wallet():
    """Re-import wallet with new encryption"""
    print("=" * 70)
    print("🔄 Wallet Re-import Tool")
    print("=" * 70)
    print()
    print("This will re-encrypt your wallet with the new enterprise system.")
    print()
    
    # Get database session
    db: Session = SessionLocal()
    
    try:
        # Find wallets
        wallets = db.query(Wallet).filter(
            Wallet.private_key_encrypted.isnot(None)
        ).all()
        
        if not wallets:
            print("❌ No wallets found in database")
            return False
        
        print(f"📋 Found {len(wallets)} wallet(s):")
        for i, wallet in enumerate(wallets, 1):
            print(f"  {i}. {wallet.currency_code} - {wallet.address}")
        print()
        
        # Get wallet to re-import
        if len(wallets) == 1:
            wallet = wallets[0]
            print(f"📝 Re-importing wallet: {wallet.currency_code} ({wallet.address})")
        else:
            choice = input(f"Which wallet to re-import? (1-{len(wallets)}): ").strip()
            try:
                wallet = wallets[int(choice) - 1]
            except (ValueError, IndexError):
                print("❌ Invalid choice")
                return False
        
        print()
        print("⚠️  You need the private key for this wallet.")
        print()
        
        # Get private key from user
        private_key = getpass("Enter private key (0x...): ").strip()
        
        if not private_key:
            print("❌ Private key is required")
            return False
        
        if not private_key.startswith("0x"):
            print("❌ Private key must start with 0x")
            return False
        
        print()
        print("🔄 Re-encrypting wallet...")
        
        try:
            # Encrypt with new system
            new_encrypted = encrypt_private_key(private_key)
            
            # Update wallet
            wallet.private_key_encrypted = new_encrypted
            
            # Commit changes
            db.commit()
            
            print("✅ Wallet re-encrypted successfully!")
            print()
            print(f"📋 Wallet Details:")
            print(f"   Address: {wallet.address}")
            print(f"   Currency: {wallet.currency_code}")
            print(f"   Balance: {wallet.balance}")
            print()
            print("🎉 You can now send transactions!")
            print()
            
            return True
            
        except Exception as e:
            db.rollback()
            print(f"❌ Failed to re-encrypt: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    success = reimport_wallet()
    
    if success:
        print("=" * 70)
        print("Next Steps:")
        print("1. ✅ Wallet re-imported")
        print("2. 🔄 Restart backend: python backend/main.py")
        print("3. ✅ Try sending transaction again")
        print("=" * 70)
    else:
        print()
        print("⚠️  Re-import failed. Options:")
        print("1. Check private key is correct")
        print("2. Or create a new wallet")
    
    sys.exit(0 if success else 1)
