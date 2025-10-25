"""
Test Wallet Creation
Creates wallets for existing users and tests the wallet system
"""
import requests
import json

BASE_URL = "http://localhost:9000"

def test_wallet_system():
    """Complete wallet system test"""
    
    print("="*80)
    print("🚀 Testing DPG Wallet System")
    print("="*80)
    
    # Login first to get token
    login_data = {
        "email": "test@example.com",
        "password": "Test123456"
    }
    
    print("\n1️⃣ Logging in...")
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"   ❌ Login failed: {response.json()}")
        return
    
    token_data = response.json()
    access_token = token_data['access_token']
    print(f"   ✅ Logged in successfully!")
    print(f"   🔑 Token: {access_token[:30]}...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Create ETH wallet
    print("\n2️⃣ Creating Ethereum Wallet...")
    eth_wallet = {
        "currency_code": "ETH",
        "wallet_type": "crypto"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/wallets/create",
        json=eth_wallet,
        headers=headers
    )
    
    if response.status_code == 201:
        wallet = response.json()
        print("   ✅ ETH Wallet created!")
        print(f"   💰 Currency: {wallet['currency_code']}")
        print(f"   📍 Address: {wallet['address']}")
        print(f"   🆔 Wallet ID: {wallet['id']}")
        print(f"   💵 Balance: {wallet['balance']}")
        eth_wallet_id = wallet['id']
    else:
        print(f"   ❌ Failed: {response.json()}")
        eth_wallet_id = None
    
    # Create USD fiat wallet
    print("\n3️⃣ Creating USD Fiat Wallet...")
    usd_wallet = {
        "currency_code": "USD",
        "wallet_type": "fiat"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/wallets/create",
        json=usd_wallet,
        headers=headers
    )
    
    if response.status_code == 201:
        wallet = response.json()
        print("   ✅ USD Wallet created!")
        print(f"   💰 Currency: {wallet['currency_code']}")
        print(f"   💵 Balance: {wallet['balance']}")
    else:
        print(f"   ❌ Failed: {response.json()}")
    
    # Get all wallets
    print("\n4️⃣ Fetching all user wallets...")
    response = requests.get(
        f"{BASE_URL}/api/v1/wallets/",
        headers=headers
    )
    
    if response.status_code == 200:
        wallets = response.json()
        print(f"   ✅ Found {len(wallets)} wallet(s)")
        for idx, wallet in enumerate(wallets, 1):
            print(f"\n   Wallet #{idx}:")
            print(f"      💰 {wallet['currency_code']} ({wallet['wallet_type']})")
            print(f"      💵 Balance: {wallet['balance']}")
            if wallet.get('address'):
                print(f"      📍 Address: {wallet['address']}")
    else:
        print(f"   ❌ Failed: {response.json()}")
    
    # Check live blockchain balance (if ETH wallet created)
    if eth_wallet_id:
        print("\n5️⃣ Checking live blockchain balance...")
        response = requests.get(
            f"{BASE_URL}/api/v1/wallets/{eth_wallet_id}/balance",
            headers=headers
        )
        
        if response.status_code == 200:
            balance_info = response.json()
            print("   ✅ Balance retrieved!")
            print(f"   📊 Database Balance: {balance_info.get('balance_database', 'N/A')}")
            print(f"   ⛓️  Blockchain Balance: {balance_info.get('balance_blockchain', 'N/A')} ETH")
            print(f"   🌐 Network: {balance_info.get('network', 'N/A')}")
        else:
            print(f"   ⚠️  Balance check failed (expected for new wallets)")
    
    print("\n" + "="*80)
    print("✨ Wallet system test complete!")
    print("="*80)

if __name__ == "__main__":
    try:
        test_wallet_system()
    except Exception as e:
        print(f"\n❌ Error: {e}")
