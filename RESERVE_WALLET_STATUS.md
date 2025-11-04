# ✅ Reserve Wallet Configuration - UPDATED

## Current Configuration

**Reserve Wallet Address:** `0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765`

This is your DPG wallet (umerdon67@gmail.com) that currently holds:
- 💰 **0.049 ETH** on Sepolia testnet

### All Currencies Using Same Wallet:
- ✅ ETH: `0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765`
- ✅ USDT: `0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765`
- ✅ USDC: `0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765`
- ✅ MATIC: `0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765`

## What This Means

### ✅ For Testing (Current Setup):
- Your Proof of Reserves will verify against this wallet
- On-chain balance check will show ~0.049 ETH
- This is perfect for development and testing

### 🔍 Verification Links:
- **Etherscan (Sepolia):** https://sepolia.etherscan.io/address/0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765
- Click "Proof of Reserves" in your app to see live verification

## How to Change (If Needed)

### Option 1: Use Your MetaMask Wallet Instead
1. Open MetaMask
2. Copy your wallet address
3. Edit `backend/reserve_config.py`
4. Replace `0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765` with your MetaMask address

### Option 2: Add Multiple Wallets
Edit `backend/reserve_config.py`:
```python
RESERVE_WALLETS = {
    'ETH': [
        '0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765',  # Your DPG wallet
        '0xYourMetaMaskWallet',                        # Your MetaMask
        '0xAnotherColdWallet',                         # Cold storage
    ],
}
```

### Option 3: Use Environment Variables (.env)
Add to your `.env` file:
```bash
ETH_RESERVE_WALLETS=0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765
USDT_RESERVE_WALLETS=0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765
```

## Quick Commands

### Check Current Configuration:
```bash
cd backend
python reserve_config.py
```

### Check All Your Wallets:
```bash
cd backend
python check_wallets.py
```

### Test Proof of Reserves:
1. Start backend: `python main.py`
2. Open frontend: `http://localhost:3000`
3. Login and click "Proof of Reserves"
4. Should show on-chain verification with your wallet balance

## Notes

- ✅ Using your own DPG wallet is perfect for testing
- ✅ The system will verify blockchain balance matches database
- ⚠️ For production, consider using dedicated reserve wallets
- ⚠️ For production, use multiple wallets (hot + cold storage)
- ⚠️ For production, enable multi-signature wallets

---

**Last Updated:** November 5, 2025
**Configuration File:** `backend/reserve_config.py`
**Your Wallet:** `0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765` ✅
