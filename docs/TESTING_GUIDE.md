# 🧪 Testing Guide - Blockchain Integration

**Last Updated:** November 2, 2025  
**Status:** Ready for Testing

---

## 🚀 Quick Start - Run the Test Suite

### Prerequisites

1. **Backend Running:**
   ```powershell
   cd backend
   python main.py
   ```
   Server should be running on `http://localhost:9000`

2. **Testnet ETH Available:**
   - You need testnet ETH in a wallet
   - Get free ETH from: https://sepoliafaucet.com
   - Minimum recommended: 0.01 ETH

---

## 📋 Running the Comprehensive Test

### Option 1: Run Full Test Suite (Recommended)

```powershell
cd backend
python test_blockchain.py
```

**What this tests:**
1. ✅ User Registration
2. ✅ User Login
3. ✅ Wallet Creation
4. ✅ Balance Sync with Blockchain
5. ✅ Send Real Transaction
6. ✅ Transaction Status Tracking
7. ✅ Transaction History

**Expected Output:**
```
============================================================
🧪 DPG BLOCKCHAIN INTEGRATION TEST
============================================================

STEP 1: Authentication
✅ Registered user: test_1730561234@dpg.finance

STEP 2: Create Crypto Wallet
✅ Wallet created: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
ℹ️  Wallet ID: uuid-here

STEP 3: List All Wallets
✅ Found 1 wallets
  - ETH: 0.297000000000000000 (0x742d35Cc6634C0532...)

STEP 4: Sync Balance with Blockchain
✅ Balance synced!
  Old balance: 0 ETH
  New balance: 0.297 ETH
  Difference: 0.297 ETH

STEP 5: Send Blockchain Transaction
⚠️  Sending 0.001 ETH to 0xd8dA6BF26964aF9D7e...
⚠️  This is a REAL transaction on Sepolia testnet!
✅ Transaction sent to blockchain!
  TX Hash: 0xabc123...
  Explorer: https://sepolia.etherscan.io/tx/0xabc123...
  Gas Fee: 0.000021 ETH

STEP 6: Monitor Transaction Status
ℹ️  Waiting for transaction confirmation...
  Check #1/10...
⚠️  Transaction still pending...
  Check #2/10...
✅ Transaction confirmed!
  Confirmations: 2
  Block: 4567890

STEP 7: Transaction History
✅ Found 1 transactions
  - withdrawal: 0.001000000000000000 (completed)
    Hash: 0xabc123...

============================================================
📊 TEST SUMMARY
============================================================
✅ All tests completed!

🔗 View your transaction:
   https://sepolia.etherscan.io/tx/0xabc123...

💼 Your wallet address:
   0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

---

## 🔧 Option 2: Manual API Testing

### 1. Register/Login

```bash
# Register
curl -X POST http://localhost:9000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@dpg.finance",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@dpg.finance&password=TestPass123!"
```

**Save the `access_token` from response!**

### 2. Create Wallet

```bash
curl -X POST http://localhost:9000/api/v1/wallets/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "currency_code": "ETH",
    "wallet_type": "crypto"
  }'
```

**Save the `id` and `address` from response!**

### 3. Sync Balance

```bash
curl -X POST http://localhost:9000/api/v1/transactions/sync-balance/WALLET_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Send Transaction

```bash
curl -X POST http://localhost:9000/api/v1/transactions/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_id": "WALLET_ID",
    "to_address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    "amount": 0.001,
    "network": "sepolia",
    "description": "Test transaction"
  }'
```

**Save the `tx_hash` from response!**

### 5. Check Transaction Status

```bash
curl -X GET "http://localhost:9000/api/v1/transactions/status/TX_HASH?network=sepolia" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. View Transaction History

```bash
curl -X GET http://localhost:9000/api/v1/transactions/history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 Test Scenarios

### Scenario 1: Happy Path
1. Register new user ✅
2. Create ETH wallet ✅
3. Import wallet with testnet ETH ✅
4. Sync balance ✅
5. Send 0.001 ETH ✅
6. Verify on Etherscan ✅
7. Check transaction confirms ✅

### Scenario 2: Error Handling
1. Try to send without ETH (should fail with clear message) ✅
2. Try to send to invalid address (should fail) ✅
3. Try to send more than balance (should fail) ✅
4. Try to send without gas fee (should calculate and warn) ✅

### Scenario 3: Edge Cases
1. Send very small amount (0.0001 ETH) ✅
2. Send with exact balance minus gas ✅
3. Check status of non-existent tx_hash ✅
4. Sync balance multiple times ✅

---

## 📊 Expected Results

### ✅ Success Indicators:
- User can register and login
- Wallet creates with valid Ethereum address
- Balance syncs from blockchain correctly
- Transaction sends and returns tx_hash
- Etherscan shows transaction
- Status endpoint tracks confirmations
- Database updates transaction status
- Transaction appears in history

### ❌ Failure Indicators:
- Connection errors to Infura
- "Insufficient balance" errors
- Gas estimation failures
- Transaction reverts
- Database errors

---

## 🐛 Common Issues & Solutions

### Issue 1: "Cannot connect to Sepolia"
**Solution:** Check your `.env` file has valid Infura API key
```
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
```

### Issue 2: "Insufficient blockchain balance"
**Solution:** 
- Get testnet ETH from https://sepoliafaucet.com
- Make sure you're checking the correct wallet address
- Run sync-balance endpoint first

### Issue 3: "Transaction pending forever"
**Solution:**
- Sepolia can be slow sometimes (5-30 seconds)
- Check Etherscan to see real status
- Gas price might be too low (rare on testnet)

### Issue 4: "Wallet not found"
**Solution:**
- Make sure you're using the correct wallet_id
- Verify wallet belongs to logged-in user
- Check if wallet was deleted

---

## 📸 Testing Checklist

Before marking tests complete:

- [ ] Screenshot of successful registration
- [ ] Screenshot of wallet creation with address
- [ ] Screenshot of balance sync (showing real balance)
- [ ] Screenshot of send transaction response
- [ ] Screenshot of Etherscan showing transaction
- [ ] Screenshot of transaction status (confirmed)
- [ ] Screenshot of transaction history
- [ ] Note any errors encountered
- [ ] Document gas fees paid
- [ ] Verify database matches blockchain

---

## 🎓 Understanding the Flow

### What Happens When You Send?

1. **Frontend:** User clicks "Send"
2. **API:** POST /transactions/send
3. **Validation:** 
   - Check user owns wallet
   - Check sufficient balance
   - Validate address format
4. **Gas Estimation:**
   - Query blockchain for current gas price
   - Calculate total needed (amount + gas)
5. **Key Decryption:**
   - Decrypt private key from database
   - Use Fernet encryption (secure)
6. **Transaction Building:**
   - Get nonce from blockchain
   - Build transaction object
   - Sign with private key
7. **Blockchain Send:**
   - Send to Sepolia via Infura
   - Receive tx_hash
8. **Database Update:**
   - Store transaction with tx_hash
   - Mark status as "pending"
   - Update wallet balance
9. **Response:**
   - Return tx_hash and Etherscan link
10. **Confirmation (later):**
    - User or cron job checks status
    - Update from "pending" → "confirmed"

---

## 🚀 Next Steps After Testing

Once all tests pass:

1. **Mark TODO complete** ✅
2. **Document results** in TEST_RECORDS.md
3. **Move to UI improvements**
4. **Add ERC-20 token support (USDT, USDC)**
5. **Deploy $DPG token to testnet (Nov 6-8)**

---

## 💡 Tips for Testing

- **Use small amounts** (0.001 ETH) to conserve testnet ETH
- **Wait for confirmations** before testing again (avoid nonce issues)
- **Check Etherscan** if anything seems wrong
- **Keep your test wallet** for future tests (don't delete)
- **Document everything** for the audit later

---

## 📞 Need Help?

If tests fail:
1. Check the console logs in terminal
2. Check browser console for frontend errors
3. Verify .env file configuration
4. Ensure PostgreSQL is running
5. Make sure port 9000 is available
6. Try restarting the backend server

---

**Happy Testing! 🎉**

Remember: These are REAL blockchain transactions, so double-check everything before sending!
