"""
Quick Fix: Delete Old Wallet and Create Fresh One
This is the simplest solution for development/testnet wallets
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from database import SessionLocal
from models import Wallet
from wallet_service import generate_ethereum_wallet, encrypt_private_key

def quick_fix():
    """Delete old wallet and create new one with enterprise encryption"""
    print("=" * 70)
    print("🔧 Quick Fix: Fresh Wallet with Enterprise Encryption")
    print("=" * 70)
    print()
    
    db = SessionLocal()
    
    try:
        # Find old wallets
        old_wallets = db.query(Wallet).filter(
            Wallet.private_key_encrypted.isnot(None)
        ).all()
        
        print(f"📋 Found {len(old_wallets)} old wallet(s):")
        for w in old_wallets:
            print(f"   - {w.currency_code}: {w.address} (Balance: {w.balance} ETH)")
        print()
        
        # Get user info for new wallet
        user_id = old_wallets[0].user_id if old_wallets else None
        
        if not user_id:
            print("❌ No user found")
            return False
        
        print("⚠️  This will:")
        print("   1. Delete the old wallet (encrypted with old key)")
        print("   2. Create a new wallet (with enterprise encryption)")
        print("   3. You'll need to get testnet ETH again from faucet")
        print()
        
        response = input("Continue? (yes/no): ").lower().strip()
        
        if response != 'yes':
            print("\n✅ Operation cancelled")
            return False
        
        print()
        print("🗑️  Deleting old wallet...")
        
        # Delete old wallets
        for w in old_wallets:
            db.delete(w)
        db.commit()
        
        print("✅ Old wallet deleted")
        print()
        print("🔄 Creating new wallet with enterprise encryption...")
        
        # Generate new wallet
        address, private_key = generate_ethereum_wallet()
        
        # Encrypt with new system
        encrypted_key = encrypt_private_key(private_key)
        
        # Create wallet record
        new_wallet = Wallet(
            user_id=user_id,
            currency_code="ETH",
            wallet_type="crypto",
            balance=0,
            address=address,
            private_key_encrypted=encrypted_key
        )
        
        db.add(new_wallet)
        db.commit()
        db.refresh(new_wallet)
        
        print("✅ New wallet created!")
        print()
        print("=" * 70)
        print("🎉 SUCCESS!")
        print("=" * 70)
        print()
        print(f"📋 New Wallet Details:")
        print(f"   Address: {address}")
        print(f"   Private Key: {private_key[:20]}...{private_key[-10:]}")
        print(f"   Balance: 0 ETH (need to get testnet ETH)")
        print()
        print("=" * 70)
        print("📝 IMPORTANT: Save Your Private Key!")
        print("=" * 70)
        print(f"\n{private_key}\n")
        print("⚠️  Copy this private key to a safe place!")
        print("⚠️  You'll need it if you want to import this wallet elsewhere")
        print()
        print("=" * 70)
        print("Next Steps:")
        print("=" * 70)
        print(f"1. 💰 Get testnet ETH: https://sepoliafaucet.com")
        print(f"   Your address: {address}")
        print(f"2. 🔄 Restart backend: python backend/main.py")
        print(f"3. ✅ Try sending transaction again")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    success = quick_fix()
    sys.exit(0 if success else 1)
