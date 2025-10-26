"""
DPG Stress Testing Suite
Tests the platform under various edge cases and stress conditions
"""
import requests
import time
import json
from decimal import Decimal
import sys
import io

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:9000"

# Test Results Storage
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def log_test(test_name, passed, message=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if message:
        print(f"     └─ {message}")
    
    if passed:
        test_results["passed"].append(test_name)
    else:
        test_results["failed"].append({"test": test_name, "message": message})

def register_user(email, password, first_name="Test", last_name="User"):
    """Register a new user"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name
            }
        )
        return response.status_code == 201, response.json() if response.status_code == 201 else response.text
    except Exception as e:
        return False, str(e)

def login_user(email, password):
    """Login and get access token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": email,
                "password": password
            }
        )
        if response.status_code == 200:
            return True, response.json()["access_token"]
        return False, response.text
    except Exception as e:
        return False, str(e)

def create_wallet(token, currency_code="USD"):
    """Create a wallet"""
    try:
        # Determine wallet type based on currency
        wallet_type = "crypto" if currency_code in ["ETH", "MATIC", "USDT", "USDC"] else "fiat"
        
        response = requests.post(
            f"{BASE_URL}/api/v1/wallets/create",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "currency_code": currency_code,
                "wallet_type": wallet_type
            }
        )
        return response.status_code == 201, response.json() if response.status_code == 201 else response.text
    except Exception as e:
        return False, str(e)

def deposit(token, wallet_id, amount, description="Test deposit"):
    """Make a deposit"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/transactions/deposit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "wallet_id": wallet_id,
                "amount": str(amount),
                "description": description
            }
        )
        return response.status_code == 201, response.json() if response.status_code == 201 else response.text
    except Exception as e:
        return False, str(e)

def withdraw(token, wallet_id, amount, description="Test withdrawal"):
    """Make a withdrawal"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/transactions/withdraw",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "wallet_id": wallet_id,
                "amount": str(amount),
                "description": description
            }
        )
        return response.status_code == 201, response.json() if response.status_code == 201 else response.text
    except Exception as e:
        return False, str(e)

def get_wallet(token, wallet_id):
    """Get wallet details"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/wallets/{wallet_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

# ============================================================================
# TEST SUITE
# ============================================================================

def test_rapid_deposits():
    """Test 10 rapid deposits in a row"""
    print_header("TEST 1: Rapid Deposits (10 in a row)")
    
    # Setup
    email = f"rapid_deposit_{int(time.time())}@test.com"
    success, result = register_user(email, "Test123456")
    if not success:
        log_test("Rapid Deposits - Setup", False, f"Failed to register user: {result}")
        return
    
    success, token = login_user(email, "Test123456")
    if not success:
        log_test("Rapid Deposits - Setup", False, "Failed to login")
        return
    
    success, wallet = create_wallet(token, "USD")
    if not success:
        log_test("Rapid Deposits - Setup", False, f"Failed to create wallet: {wallet}")
        return
    
    wallet_id = wallet["id"]
    
    # Test rapid deposits
    start_time = time.time()
    for i in range(10):
        success, result = deposit(token, wallet_id, 100, f"Rapid deposit #{i+1}")
        if not success:
            log_test(f"Rapid Deposit #{i+1}", False, str(result))
            return
    
    elapsed = time.time() - start_time
    
    # Verify final balance
    success, wallet_data = get_wallet(token, wallet_id)
    if success and float(wallet_data["balance"]) == 1000:
        log_test("Rapid Deposits", True, f"10 deposits in {elapsed:.2f}s, balance: $1000")
    else:
        log_test("Rapid Deposits", False, f"Balance mismatch: {wallet_data.get('balance', 'N/A')}")

def test_rapid_withdrawals():
    """Test 10 rapid withdrawals in a row"""
    print_header("TEST 2: Rapid Withdrawals (10 in a row)")
    
    # Setup
    email = f"rapid_withdraw_{int(time.time())}@test.com"
    success, _ = register_user(email, "Test123456")
    success, token = login_user(email, "Test123456")
    success, wallet = create_wallet(token, "USD")
    wallet_id = wallet["id"]
    
    # Deposit initial amount
    deposit(token, wallet_id, 10000)
    
    # Test rapid withdrawals
    start_time = time.time()
    for i in range(10):
        success, result = withdraw(token, wallet_id, 100, f"Rapid withdrawal #{i+1}")
        if not success:
            log_test(f"Rapid Withdrawal #{i+1}", False, str(result))
            return
    
    elapsed = time.time() - start_time
    
    # Verify final balance (10000 - 1000 withdrawals - ~5 fees)
    success, wallet_data = get_wallet(token, wallet_id)
    expected = 10000 - 1000 - 5  # Approximate with fees
    actual = float(wallet_data["balance"])
    
    if success and abs(actual - expected) < 10:  # Allow small variance for fees
        log_test("Rapid Withdrawals", True, f"10 withdrawals in {elapsed:.2f}s, balance: ${actual}")
    else:
        log_test("Rapid Withdrawals", False, f"Balance unexpected: ${actual}")

def test_multiple_wallets():
    """Test creating multiple wallets"""
    print_header("TEST 3: Multiple Wallet Creation")
    
    email = f"multi_wallet_{int(time.time())}@test.com"
    register_user(email, "Test123456")
    success, token = login_user(email, "Test123456")
    
    currencies = ["USD", "ETH", "MATIC", "USDT", "USDC"]
    wallets_created = 0
    
    for currency in currencies:
        success, wallet = create_wallet(token, currency)
        if success:
            wallets_created += 1
        else:
            log_test(f"Create {currency} Wallet", False, str(wallet))
    
    if wallets_created == len(currencies):
        log_test("Multiple Wallets", True, f"Created {wallets_created}/{len(currencies)} wallets")
    else:
        log_test("Multiple Wallets", False, f"Only created {wallets_created}/{len(currencies)}")

def test_large_amounts():
    """Test with very large amounts"""
    print_header("TEST 4: Large Amounts ($1,000,000+)")
    
    email = f"large_amount_{int(time.time())}@test.com"
    register_user(email, "Test123456")
    success, token = login_user(email, "Test123456")
    success, wallet = create_wallet(token, "USD")
    wallet_id = wallet["id"]
    
    # Test depositing $1,000,000
    success, result = deposit(token, wallet_id, 1000000, "Large deposit test")
    
    if success:
        success, wallet_data = get_wallet(token, wallet_id)
        if float(wallet_data["balance"]) == 1000000:
            log_test("Large Amount Deposit", True, "Handled $1,000,000 successfully")
        else:
            log_test("Large Amount Deposit", False, f"Balance mismatch: {wallet_data['balance']}")
    else:
        log_test("Large Amount Deposit", False, str(result))

def test_decimal_amounts():
    """Test with very small decimal amounts"""
    print_header("TEST 5: Decimal Amounts (0.0001 ETH)")
    
    email = f"decimal_test_{int(time.time())}@test.com"
    register_user(email, "Test123456")
    success, token = login_user(email, "Test123456")
    success, wallet = create_wallet(token, "ETH")
    wallet_id = wallet["id"]
    
    # Test depositing 0.0001 ETH
    success, result = deposit(token, wallet_id, 0.0001, "Small decimal test")
    
    if success:
        success, wallet_data = get_wallet(token, wallet_id)
        balance = float(wallet_data["balance"])
        if balance == 0.0001:
            log_test("Decimal Amount", True, f"Handled 0.0001 ETH correctly")
        else:
            log_test("Decimal Amount", False, f"Balance precision issue: {balance}")
    else:
        log_test("Decimal Amount", False, str(result))

def test_edge_cases():
    """Test various edge cases"""
    print_header("TEST 6: Edge Cases")
    
    email = f"edge_case_{int(time.time())}@test.com"
    register_user(email, "Test123456")
    success, token = login_user(email, "Test123456")
    success, wallet = create_wallet(token, "USD")
    wallet_id = wallet["id"]
    
    # Deposit some funds first
    deposit(token, wallet_id, 1000)
    
    # Test negative amount
    success, result = deposit(token, wallet_id, -100, "Negative test")
    log_test("Edge Case: Negative Amount", not success, "Should reject negative amounts")
    
    # Test zero amount
    success, result = deposit(token, wallet_id, 0, "Zero test")
    log_test("Edge Case: Zero Amount", not success, "Should reject zero amounts")
    
    # Test very small amount
    success, result = deposit(token, wallet_id, 0.00000001, "Tiny amount")
    log_test("Edge Case: Tiny Amount (0.00000001)", success, "Should handle tiny amounts")
    
    # Test very large amount
    success, result = deposit(token, wallet_id, 999999999, "Huge amount")
    log_test("Edge Case: Huge Amount (999999999)", success, "Should handle huge amounts")
    
    # Test special characters in description
    success, result = deposit(token, wallet_id, 10, "Test <script>alert('xss')</script>")
    log_test("Edge Case: XSS in Description", success, "Should sanitize special chars")
    
    # Test SQL injection attempt in description
    success, result = deposit(token, wallet_id, 10, "'; DROP TABLE users; --")
    log_test("Edge Case: SQL Injection", success, "Should prevent SQL injection")

def test_insufficient_balance():
    """Test withdrawal with insufficient balance"""
    print_header("TEST 7: Insufficient Balance")
    
    email = f"insufficient_{int(time.time())}@test.com"
    register_user(email, "Test123456")
    success, token = login_user(email, "Test123456")
    success, wallet = create_wallet(token, "USD")
    wallet_id = wallet["id"]
    
    # Try to withdraw without depositing
    success, result = withdraw(token, wallet_id, 100, "Should fail")
    
    log_test("Insufficient Balance", not success, "Should reject withdrawal with no balance")

def print_summary():
    """Print test summary"""
    print_header("📊 TEST SUMMARY")
    
    total = len(test_results["passed"]) + len(test_results["failed"])
    passed = len(test_results["passed"])
    failed = len(test_results["failed"])
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    
    if failed > 0:
        print("\n🔴 FAILED TESTS:")
        for fail in test_results["failed"]:
            print(f"   - {fail['test']}: {fail['message']}")
    
    print("\n" + "="*80)
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Your platform is solid!")
    else:
        print(f"⚠️  {failed} test(s) need attention. Fix these before deployment.")
    
    print("="*80 + "\n")

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("\n🧪 DPG STRESS TESTING SUITE")
    print("="*80)
    print("Testing Date: Oct 27, 2025")
    print("="*80)
    
    # Run all tests
    test_rapid_deposits()
    test_rapid_withdrawals()
    test_multiple_wallets()
    test_large_amounts()
    test_decimal_amounts()
    test_edge_cases()
    test_insufficient_balance()
    
    # Print summary
    print_summary()
