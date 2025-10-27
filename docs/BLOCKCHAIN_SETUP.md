# 🚀 Blockchain Integration Setup Guide

**Last Updated:** October 27, 2025  
**Status:** Ready for Testing (Sepolia Testnet)

---

## 📋 Prerequisites

✅ Python 3.13+ installed  
✅ Web3.py, eth-account packages installed  
✅ PostgreSQL database running  
✅ Free Infura or Alchemy account

---

## 🔧 Step 1: Get Infura API Key (FREE)

### Option A: Infura (Recommended)

1. Go to **https://infura.io**
2. Click "Sign Up" → Create free account
3. Click "Create New API Key"
4. Select "Web3 API (Ethereum, Polygon, etc.)"
5. Name it: **DPG Payment Gateway**
6. Copy your **API Key** (looks like: `abc123def456...`)

### Option B: Alchemy (Alternative)

1. Go to **https://alchemy.com**
2. Sign up for free account
3. Create new app → Ethereum → Sepolia
4. Copy your **API Key**

**Your API Key:**
```
YOUR_INFURA_KEY: _______________________________
```

---

## 🔑 Step 2: Update Environment Variables

1. Open `backend/.env` file
2. Replace `YOUR_INFURA_KEY_HERE` with your actual key:

```env
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_ACTUAL_KEY_HERE
```

**Example:**
```env
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/abc123def456ghi789
```

---

## 💰 Step 3: Get Testnet ETH (FREE)

You need testnet ETH to pay for gas fees when sending transactions.

### Sepolia Faucets (Choose ONE):

1. **Alchemy Sepolia Faucet** (Easiest)
   - https://sepoliafaucet.com
   - Connect wallet → Get 0.5 ETH
   - Wait 1-2 minutes

2. **Infura Faucet**
   - https://www.infura.io/faucet/sepolia
   - Login with Infura account
   - Enter wallet address → Get 0.5 ETH

3. **Chainlink Faucet**
   - https://faucets.chain.link/sepolia
   - Connect GitHub account
   - Get 0.1 ETH

### Get a Wallet Address:

**Option 1: Use MetaMask (Easy)**
1. Install MetaMask extension
2. Create new wallet
3. Switch network to "Sepolia"
4. Copy your address (0x...)

**Option 2: Generate Programmatically**
```bash
cd backend
python blockchain_service.py
```
This will generate a new wallet for you!

**Your Testnet Wallet:**
```
Address: 0x_______________________________
Private Key: 0x_____________________________ (KEEP SECRET!)
```

---

## 🧪 Step 4: Test Blockchain Connection

```bash
cd backend
python blockchain_service.py
```

**Expected Output:**
```
🧪 Testing Blockchain Service

✅ Connected to Sepolia Testnet
✅ Address validation: True
✅ Balance check: 0.5 ETH
✅ Generated wallet: 0x...
✅ All tests passed!
```

---

## 🔐 Step 5: Configure Master Wallet

The master wallet pays for gas fees when sending user transactions.

1. Generate a new wallet (from Step 3)
2. Fund it with testnet ETH (0.5 ETH is enough)
3. Update `.env`:

```env
MASTER_WALLET_PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
```

⚠️ **IMPORTANT:**
- ✅ Use a NEW wallet (don't use your personal wallet)
- ✅ Only testnet funds (Sepolia ETH has NO real value)
- ✅ NEVER commit `.env` to GitHub
- ✅ Generate different wallet for mainnet later

---

## 🚀 Step 6: Update Send Endpoint

The `/send` endpoint is already created but needs blockchain integration enabled.

**File:** `backend/transaction_routes.py`

Replace the mock implementation with real blockchain calls (code already prepared in `blockchain_service.py`).

---

## 📊 Step 7: Test Real Blockchain Transaction

### Test with Frontend:

1. Start server: `.\run_server.bat`
2. Open browser → http://localhost:5500
3. Click "Transfer Between Wallets"
4. Switch to "Send to Address" tab
5. Enter:
   - From: Your ETH wallet
   - To Address: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb` (test address)
   - Amount: `0.01` ETH
   - Network: Sepolia
6. Click Send
7. ✅ Check Etherscan: https://sepolia.etherscan.io

---

## 🔍 Verify Transaction

After sending, you'll get a transaction hash like:
```
0xabc123...def456
```

**Check on Etherscan:**
1. Go to https://sepolia.etherscan.io
2. Paste your tx hash in search
3. See status: Pending → Success (takes 15-30 seconds)

---

## 📈 Next Steps

### Phase 1: Testnet Testing (Oct 27 - Nov 3)
- ✅ Send ETH on Sepolia
- ✅ Test different amounts
- ✅ Check gas fees
- ✅ Verify balances update

### Phase 2: ERC-20 Tokens (Nov 4-6)
- Add USDT/USDC support
- Smart contract interactions
- Token transfers

### Phase 3: Mainnet (Nov 7+)
- Switch to Ethereum mainnet
- Real money transactions
- Production security audit

---

## 🆘 Troubleshooting

### Error: "Cannot connect to Sepolia"
- ✅ Check Infura API key in `.env`
- ✅ Verify internet connection
- ✅ Try Alchemy instead of Infura

### Error: "Insufficient funds"
- ✅ Get more testnet ETH from faucet
- ✅ Check wallet balance: `bc.get_balance('0x...')`

### Error: "Invalid address"
- ✅ Address must start with `0x`
- ✅ Must be 42 characters total
- ✅ Use checksum address

### Transaction stuck on "Pending"
- ✅ Normal! Wait 1-2 minutes
- ✅ Check Sepolia network status
- ✅ Increase gas price if urgent

---

## 🔗 Useful Links

- **Sepolia Etherscan:** https://sepolia.etherscan.io
- **Infura Dashboard:** https://app.infura.io
- **Alchemy Dashboard:** https://dashboard.alchemy.com
- **Web3.py Docs:** https://web3py.readthedocs.io
- **Ethereum Gas Tracker:** https://etherscan.io/gastracker

---

## ✅ Checklist Before Going Live

- [ ] Infura API key configured
- [ ] Master wallet funded with testnet ETH
- [ ] Blockchain service tested
- [ ] Send endpoint integrated
- [ ] Real transaction sent successfully
- [ ] Etherscan verification working
- [ ] Error handling tested
- [ ] Gas fee estimation accurate
- [ ] Balance updates correctly
- [ ] UI shows transaction status

---

**Ready to integrate?** Let's update the `/send` endpoint next! 🚀
