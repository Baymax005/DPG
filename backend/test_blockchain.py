"""
Test Script for Blockchain Integration
Tests real blockchain transactions on Sepolia testnet
"""
import requests
import json
from decimal import Decimal
import time

# Configuration
BASE_URL = "http://localhost:9000"
API_VERSION = "v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

class DPGTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.user_id = None
        self.wallet_id = None
        self.wallet_address = None
        
    def register(self, email, password, first_name, last_name):
        """Register a new user"""
        print_info("Registering new user...")
        url = f"{self.base_url}/api/{API_VERSION}/auth/register"
        data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name
        }
        
        response = requests.post(url, json=data)
        if response.status_code == 201:
            result = response.json()
            self.token = result['access_token']
            self.user_id = result['user']['id']
            print_success(f"Registered user: {email}")
            return True
        else:
            print_error(f"Registration failed: {response.text}")
            return False
    
    def login(self, email, password):
        """Login existing user"""
        print_info("Logging in...")
        url = f"{self.base_url}/api/{API_VERSION}/auth/login"
        data = {
            "username": email,
            "password": password
        }
        
        response = requests.post(url, data=data)
        if response.status_code == 200:
            result = response.json()
            self.token = result['access_token']
            print_success(f"Logged in: {email}")
            return True
        else:
            print_error(f"Login failed: {response.text}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def create_wallet(self, currency="ETH"):
        """Create a new crypto wallet"""
        print_info(f"Creating {currency} wallet...")
        url = f"{self.base_url}/api/{API_VERSION}/wallets/create"
        data = {
            "currency_code": currency,
            "wallet_type": "crypto"
        }
        
        response = requests.post(url, json=data, headers=self.get_headers())
        if response.status_code == 201:
            result = response.json()
            self.wallet_id = result['id']
            self.wallet_address = result['address']
            print_success(f"Wallet created: {self.wallet_address}")
            print_info(f"Wallet ID: {self.wallet_id}")
            return True
        else:
            print_error(f"Wallet creation failed: {response.text}")
            return False
    
    def get_wallets(self):
        """Get all user wallets"""
        print_info("Fetching wallets...")
        url = f"{self.base_url}/api/{API_VERSION}/wallets/"
        
        response = requests.get(url, headers=self.get_headers())
        if response.status_code == 200:
            wallets = response.json()
            print_success(f"Found {len(wallets)} wallets")
            for wallet in wallets:
                print(f"  - {wallet['currency_code']}: {wallet['balance']} ({wallet['address'][:20]}...)")
            return wallets
        else:
            print_error(f"Failed to fetch wallets: {response.text}")
            return []
    
    def sync_balance(self, wallet_id):
        """Sync wallet balance with blockchain"""
        print_info("Syncing balance with blockchain...")
        url = f"{self.base_url}/api/{API_VERSION}/transactions/sync-balance/{wallet_id}"
        
        response = requests.post(url, headers=self.get_headers())
        if response.status_code == 200:
            result = response.json()
            print_success(f"Balance synced!")
            print(f"  Old balance: {result['old_balance']} ETH")
            print(f"  New balance: {result['new_balance']} ETH")
            print(f"  Difference: {result['difference']} ETH")
            return result
        else:
            print_error(f"Balance sync failed: {response.text}")
            return None
    
    def send_transaction(self, to_address, amount, network="sepolia"):
        """Send blockchain transaction"""
        print_info(f"Sending {amount} ETH to {to_address[:20]}...")
        url = f"{self.base_url}/api/{API_VERSION}/transactions/send"
        data = {
            "wallet_id": self.wallet_id,
            "to_address": to_address,
            "amount": amount,
            "network": network,
            "description": "Test transaction from DPG"
        }
        
        response = requests.post(url, json=data, headers=self.get_headers())
        if response.status_code == 201:
            result = response.json()
            print_success("Transaction sent to blockchain!")
            print(f"  TX Hash: {result['tx_hash']}")
            print(f"  Explorer: {result['explorer_url']}")
            print(f"  Gas Fee: {result['gas_fee']} ETH")
            return result
        else:
            print_error(f"Transaction failed: {response.text}")
            return None
    
    def check_tx_status(self, tx_hash, network="sepolia"):
        """Check transaction status"""
        print_info("Checking transaction status...")
        url = f"{self.base_url}/api/{API_VERSION}/transactions/status/{tx_hash}"
        params = {"network": network}
        
        response = requests.get(url, params=params, headers=self.get_headers())
        if response.status_code == 200:
            result = response.json()
            status = result['status']
            
            if status == 'confirmed':
                print_success(f"Transaction confirmed!")
                print(f"  Confirmations: {result.get('confirmations', 0)}")
                print(f"  Block: {result.get('block_number', 'N/A')}")
            elif status == 'pending':
                print_warning("Transaction still pending...")
            else:
                print_error(f"Transaction failed!")
            
            return result
        else:
            print_error(f"Status check failed: {response.text}")
            return None
    
    def get_transactions(self):
        """Get transaction history"""
        print_info("Fetching transaction history...")
        url = f"{self.base_url}/api/{API_VERSION}/transactions/history"
        
        response = requests.get(url, headers=self.get_headers())
        if response.status_code == 200:
            transactions = response.json()
            print_success(f"Found {len(transactions)} transactions")
            for tx in transactions[:5]:  # Show last 5
                print(f"  - {tx['type']}: {tx['amount']} ({tx['status']})")
                if tx.get('tx_hash'):
                    print(f"    Hash: {tx['tx_hash'][:20]}...")
            return transactions
        else:
            print_error(f"Failed to fetch transactions: {response.text}")
            return []


def main():
    """Main test flow"""
    print("\n" + "="*60)
    print("🧪 DPG BLOCKCHAIN INTEGRATION TEST")
    print("="*60 + "\n")
    
    tester = DPGTester()
    
    # Test user credentials
    test_email = f"test_{int(time.time())}@dpg.finance"
    test_password = "TestPass123!"
    
    print("📝 Test Configuration:")
    print(f"  Email: {test_email}")
    print(f"  API: {BASE_URL}")
    print("\n")
    
    # Step 1: Register or Login
    print("=" * 60)
    print("STEP 1: Authentication")
    print("=" * 60)
    if not tester.register(test_email, test_password, "Test", "User"):
        # Try login if registration fails (user might already exist)
        if not tester.login(test_email, test_password):
            print_error("Authentication failed. Exiting.")
            return
    print()
    
    # Step 2: Create Wallet
    print("=" * 60)
    print("STEP 2: Create Crypto Wallet")
    print("=" * 60)
    if not tester.create_wallet("ETH"):
        print_error("Wallet creation failed. Exiting.")
        return
    print()
    
    # Step 3: Get Wallets
    print("=" * 60)
    print("STEP 3: List All Wallets")
    print("=" * 60)
    wallets = tester.get_wallets()
    if wallets:
        # Use the first ETH wallet
        eth_wallet = next((w for w in wallets if w['currency_code'] == 'ETH'), None)
        if eth_wallet:
            tester.wallet_id = eth_wallet['id']
            tester.wallet_address = eth_wallet['address']
    print()
    
    # Step 4: Sync Balance
    print("=" * 60)
    print("STEP 4: Sync Balance with Blockchain")
    print("=" * 60)
    balance_info = tester.sync_balance(tester.wallet_id)
    if balance_info:
        current_balance = Decimal(balance_info['new_balance'])
        
        if current_balance <= 0:
            print_warning("\n⚠️  WALLET HAS NO ETH!")
            print(f"Please send testnet ETH to: {tester.wallet_address}")
            print("Get free testnet ETH from: https://sepoliafaucet.com")
            print("\nOnce you have ETH, run this test again.\n")
            return
    print()
    
    # Step 5: Send Transaction
    print("=" * 60)
    print("STEP 5: Send Blockchain Transaction")
    print("=" * 60)
    
    # Test recipient address (Vitalik's address for testing)
    test_recipient = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    test_amount = 0.001  # Send 0.001 ETH
    
    print_warning(f"Sending {test_amount} ETH to {test_recipient[:20]}...")
    print_warning("This is a REAL transaction on Sepolia testnet!")
    
    tx_result = tester.send_transaction(test_recipient, test_amount)
    if not tx_result:
        print_error("Transaction failed. Exiting.")
        return
    
    tx_hash = tx_result['tx_hash']
    print()
    
    # Step 6: Check Transaction Status
    print("=" * 60)
    print("STEP 6: Monitor Transaction Status")
    print("=" * 60)
    
    print_info("Waiting for transaction confirmation...")
    for i in range(10):  # Check up to 10 times
        time.sleep(3)  # Wait 3 seconds between checks
        print(f"\n  Check #{i+1}/10...")
        status_info = tester.check_tx_status(tx_hash)
        
        if status_info and status_info['status'] in ['confirmed', 'failed']:
            break
    print()
    
    # Step 7: View Transaction History
    print("=" * 60)
    print("STEP 7: Transaction History")
    print("=" * 60)
    tester.get_transactions()
    print()
    
    # Final Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print_success("All tests completed!")
    print(f"\n🔗 View your transaction:")
    print(f"   {tx_result['explorer_url']}")
    print(f"\n💼 Your wallet address:")
    print(f"   {tester.wallet_address}")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print_error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
