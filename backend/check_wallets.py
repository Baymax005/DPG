"""
Quick utility to check your wallet addresses and update reserve config
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from reserve_config import print_reserve_config, RESERVE_WALLETS
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def check_database_wallets():
    """Check what wallets exist in your database"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            # Get all wallets
            result = conn.execute(text("""
                SELECT 
                    w.id,
                    u.email,
                    w.currency_code,
                    w.wallet_type,
                    w.address,
                    w.balance
                FROM wallets w
                JOIN users u ON w.user_id = u.id
                ORDER BY w.currency_code, w.balance DESC
            """))
            
            wallets = result.fetchall()
            
            if not wallets:
                print("\n📭 No wallets found in database yet!")
                print("   Create a wallet in the app first.\n")
                return
            
            print("\n" + "="*80)
            print("💼 WALLETS IN YOUR DATABASE")
            print("="*80)
            
            by_currency = {}
            for wallet in wallets:
                currency = wallet[2]
                if currency not in by_currency:
                    by_currency[currency] = []
                by_currency[currency].append(wallet)
            
            for currency, curr_wallets in by_currency.items():
                print(f"\n{currency} Wallets:")
                print("-" * 80)
                total_balance = 0
                
                for wallet in curr_wallets:
                    wallet_id, email, curr, wtype, address, balance = wallet
                    total_balance += float(balance)
                    
                    print(f"  📧 {email[:20]:<20} | Type: {wtype:<10} | Balance: {balance:>12} {currency}")
                    if address:
                        print(f"     🔗 Address: {address}")
                    print()
                
                print(f"  💰 TOTAL {currency}: {total_balance}")
                print("-" * 80)
            
            print("\n" + "="*80)
            
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("   Make sure your DATABASE_URL in .env is correct")


def suggest_reserve_wallet():
    """Suggest which wallet to use as reserve wallet"""
    print("\n" + "="*80)
    print("💡 HOW TO SET UP RESERVE WALLETS")
    print("="*80)
    
    print("""
OPTIONS:

1. 🦊 USE YOUR METAMASK WALLET (Recommended for testing):
   - Open MetaMask
   - Copy your wallet address (click on account name at top)
   - Update backend/reserve_config.py with that address
   
2. 🏦 CREATE A NEW DPG WALLET:
   - Log into your DPG app
   - Create a new ETH/USDT/USDC wallet
   - Use those addresses as reserve wallets
   
3. 💼 USE EXISTING DPG WALLETS:
   - Check the wallet addresses above
   - Pick one (preferably with some balance for testing)
   - Update backend/reserve_config.py

TO UPDATE:
1. Edit: backend/reserve_config.py
2. Replace '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb8' with your address
3. Or add to .env file:
   ETH_RESERVE_WALLETS=0xYourAddress
   USDT_RESERVE_WALLETS=0xYourAddress
   USDC_RESERVE_WALLETS=0xYourAddress

VERIFY:
Run this script again to confirm changes!
    """)
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n🔍 CHECKING YOUR WALLET CONFIGURATION...\n")
    
    # Show current reserve config
    print_reserve_config()
    
    # Check database wallets
    check_database_wallets()
    
    # Show suggestions
    suggest_reserve_wallet()
    
    # Check if using placeholder
    has_placeholder = False
    for currency, addresses in RESERVE_WALLETS.items():
        if '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb8' in addresses:
            has_placeholder = True
            break
    
    if has_placeholder:
        print("⚠️  WARNING: You're still using placeholder addresses!")
        print("   Update backend/reserve_config.py before using Proof of Reserves\n")
    else:
        print("✅ Reserve wallet addresses look configured!")
        print("   Make sure these are correct before going to production\n")
