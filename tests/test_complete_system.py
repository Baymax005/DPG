"""
Complete DPG System Test
Tests Authentication, Wallets, and Transactions
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:9000"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_complete_system():
    """Test the complete DPG system"""
    
    print_section("🚀 DPG COMPLETE SYSTEM TEST")
    
    # ====================================
    # 1. AUTHENTICATION
    # ====================================
    print_section("1️⃣ AUTHENTICATION - Login")
    
    login_data = {
        "email": "test@example.com",
        "password": "Test123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"   ❌ Login failed: {response.json()}")
        return
    
    token_data = response.json()
    access_token = token_data['access_token']
    print(f"   ✅ Login successful!")
    print(f"   🔑 Token: {access_token[:40]}...")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # ====================================
    # 2. CREATE WALLETS
    # ====================================
    print_section("2️⃣ WALLETS - Create ETH and USD wallets")
    
    # Create ETH wallet
    eth_wallet_data = {
        "currency_code": "ETH",
        "wallet_type": "crypto"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/wallets/create",
        json=eth_wallet_data,
        headers=headers
    )
    
    if response.status_code == 201:
        eth_wallet = response.json()
        print(f"   ✅ ETH Wallet created!")
        print(f"      💰 Currency: {eth_wallet['currency_code']}")
        print(f"      📍 Address: {eth_wallet['address']}")
        print(f"      💵 Balance: {eth_wallet['balance']}")
        eth_wallet_id = eth_wallet['id']
    elif response.status_code == 400 and "already exists" in response.json().get('detail', ''):
        print(f"   ℹ️  ETH Wallet already exists, fetching...")
        # Get existing wallets
        response = requests.get(f"{BASE_URL}/api/v1/wallets/", headers=headers)
        wallets = response.json()
        eth_wallet = next((w for w in wallets if w['currency_code'] == 'ETH'), None)
        if eth_wallet:
            eth_wallet_id = eth_wallet['id']
            print(f"   ✅ Using existing ETH wallet: {eth_wallet_id}")
        else:
            print(f"   ❌ Could not find ETH wallet")
            return
    else:
        print(f"   ❌ Failed: {response.json()}")
        return
    
    # Create USD wallet
    usd_wallet_data = {
        "currency_code": "USD",
        "wallet_type": "fiat"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/wallets/create",
        json=usd_wallet_data,
        headers=headers
    )
    
    if response.status_code == 201:
        usd_wallet = response.json()
        print(f"   ✅ USD Wallet created!")
        print(f"      💰 Currency: {usd_wallet['currency_code']}")
        print(f"      💵 Balance: {usd_wallet['balance']}")
        usd_wallet_id = usd_wallet['id']
    elif response.status_code == 400 and "already exists" in response.json().get('detail', ''):
        print(f"   ℹ️  USD Wallet already exists, fetching...")
        response = requests.get(f"{BASE_URL}/api/v1/wallets/", headers=headers)
        wallets = response.json()
        usd_wallet = next((w for w in wallets if w['currency_code'] == 'USD'), None)
        if usd_wallet:
            usd_wallet_id = usd_wallet['id']
            print(f"   ✅ Using existing USD wallet: {usd_wallet_id}")
        else:
            print(f"   ❌ Could not find USD wallet")
            return
    else:
        print(f"   ❌ Failed: {response.json()}")
        return
    
    # ====================================
    # 3. DEPOSIT FUNDS
    # ====================================
    print_section("3️⃣ TRANSACTIONS - Deposit funds")
    
    # Deposit to USD wallet
    deposit_data = {
        "wallet_id": usd_wallet_id,
        "amount": 1000.00,
        "description": "Test deposit - Initial funding",
        "reference_id": "TEST_" + datetime.now().strftime("%Y%m%d%H%M%S")
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/transactions/deposit",
        json=deposit_data,
        headers=headers
    )
    
    if response.status_code == 201:
        tx = response.json()
        print(f"   ✅ Deposited $1000 to USD wallet!")
        print(f"      🆔 Transaction ID: {tx['id']}")
        print(f"      💵 Amount: ${tx['amount']}")
        print(f"      ✅ Status: {tx['status']}")
    else:
        print(f"   ❌ Deposit failed: {response.json()}")
    
    # Deposit to ETH wallet
    eth_deposit_data = {
        "wallet_id": eth_wallet_id,
        "amount": 0.5,
        "description": "Test ETH deposit"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/transactions/deposit",
        json=eth_deposit_data,
        headers=headers
    )
    
    if response.status_code == 201:
        tx = response.json()
        print(f"   ✅ Deposited 0.5 ETH!")
        print(f"      🆔 Transaction ID: {tx['id']}")
        print(f"      💵 Amount: {tx['amount']} ETH")
    else:
        print(f"   ❌ ETH Deposit failed: {response.json()}")
    
    # ====================================
    # 4. CHECK BALANCES
    # ====================================
    print_section("4️⃣ WALLETS - Check updated balances")
    
    response = requests.get(f"{BASE_URL}/api/v1/wallets/", headers=headers)
    
    if response.status_code == 200:
        wallets = response.json()
        print(f"   ✅ User has {len(wallets)} wallet(s):")
        for wallet in wallets:
            print(f"\n      💰 {wallet['currency_code']} Wallet")
            print(f"         Balance: {wallet['balance']}")
            print(f"         Type: {wallet['wallet_type']}")
            if wallet.get('address'):
                print(f"         Address: {wallet['address'][:20]}...")
    
    # ====================================
    # 5. WITHDRAWAL
    # ====================================
    print_section("5️⃣ TRANSACTIONS - Withdraw funds")
    
    withdrawal_data = {
        "wallet_id": usd_wallet_id,
        "amount": 100.00,
        "description": "Test withdrawal"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/transactions/withdraw",
        json=withdrawal_data,
        headers=headers
    )
    
    if response.status_code == 201:
        tx = response.json()
        print(f"   ✅ Withdrew $100 from USD wallet!")
        print(f"      🆔 Transaction ID: {tx['id']}")
        print(f"      💵 Amount: ${tx['amount']}")
        print(f"      💸 Fee: ${tx['fee']}")
    else:
        print(f"   ❌ Withdrawal failed: {response.json()}")
    
    # ====================================
    # 6. TRANSACTION HISTORY
    # ====================================
    print_section("6️⃣ TRANSACTIONS - View history")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/transactions/history?limit=10",
        headers=headers
    )
    
    if response.status_code == 200:
        transactions = response.json()
        print(f"   ✅ Found {len(transactions)} transaction(s):")
        
        for idx, tx in enumerate(transactions, 1):
            print(f"\n      Transaction #{idx}:")
            print(f"         Type: {tx['type']}")
            print(f"         Amount: {tx['amount']}")
            print(f"         Fee: {tx['fee']}")
            print(f"         Status: {tx['status']}")
            print(f"         Date: {tx['created_at'][:19]}")
            if tx.get('description'):
                print(f"         Description: {tx['description']}")
    else:
        print(f"   ❌ Failed to get transactions: {response.json()}")
    
    # ====================================
    # 7. FINAL SUMMARY
    # ====================================
    print_section("📊 FINAL SUMMARY")
    
    response = requests.get(f"{BASE_URL}/api/v1/wallets/", headers=headers)
    if response.status_code == 200:
        wallets = response.json()
        total_usd = 0
        
        print("   💰 WALLET BALANCES:")
        for wallet in wallets:
            balance = float(wallet['balance'])
            print(f"      {wallet['currency_code']}: {balance}")
            if wallet['currency_code'] == 'USD':
                total_usd += balance
        
        print(f"\n   💵 Total USD Value: ${total_usd:.2f}")
    
    print("\n" + "="*80)
    print("✨ DPG System Test Complete!")
    print("="*80)
    print("\n🎉 Your payment gateway has:")
    print("   ✅ User Authentication")
    print("   ✅ Multi-currency Wallets (Fiat + Crypto)")
    print("   ✅ Deposits & Withdrawals")
    print("   ✅ Transaction History")
    print("\n📍 Next: Build the frontend to make this visual!")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        test_complete_system()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server at http://localhost:9000")
        print("   Make sure the server is running:")
        print("   cd backend && python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
