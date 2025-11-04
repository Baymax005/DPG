# 🏦 Reserve Wallet Configuration Guide

## Quick Start

### 1. Check Current Configuration
```bash
cd backend
python check_wallets.py
```

This will show:
- ✅ Current reserve wallet addresses
- 💼 All wallets in your database
- 💡 Suggestions on which address to use

### 2. Update Reserve Wallet Address

#### Option A: Edit Configuration File (Easiest)
Edit `backend/reserve_config.py`:

```python
RESERVE_WALLETS = {
    'ETH': ['0xYourActualAddress'],   # Replace this!
    'USDT': ['0xYourActualAddress'],  # Replace this!
    'USDC': ['0xYourActualAddress'],  # Replace this!
}
```

#### Option B: Use Environment Variables (Production)
Add to `.env` file:
```bash
ETH_RESERVE_WALLETS=0xYourAddress1,0xYourAddress2
USDT_RESERVE_WALLETS=0xYourAddress
USDC_RESERVE_WALLETS=0xYourAddress
```

### 3. Where to Get Your Wallet Address?

#### 🦊 Using MetaMask (Recommended for Testing):
1. Open MetaMask browser extension
2. Click on your account name at the top
3. Click the copy icon next to your address
4. Paste into `reserve_config.py`

#### 🏦 Using DPG Wallet:
1. Log into your DPG app at `http://localhost:3000`
2. Create or select a wallet
3. Copy the address shown
4. Paste into `reserve_config.py`

#### 💻 Using Database:
```bash
python check_wallets.py
```
Copy any address from the output.

### 4. Verify Configuration
```bash
python reserve_config.py
```

Should show:
```
🏦 RESERVE WALLET CONFIGURATION
==================================================
ETH:
  1. ✅ 0xYourActualAddress
USDT:
  1. ✅ 0xYourActualAddress
...
```

## Important Notes

### For Development/Testing:
- ✅ Use the same address for all currencies (ETH, USDT, USDC)
- ✅ Use your MetaMask testnet address
- ✅ Make sure the wallet has some testnet funds

### For Production:
- ⚠️ Use dedicated reserve wallets
- ⚠️ Consider using multiple wallets (hot + cold storage)
- ⚠️ Use environment variables, not hardcoded addresses
- ⚠️ Enable multi-signature wallets
- ⚠️ Regular security audits

## Example Configurations

### Single Wallet (Testing):
```python
RESERVE_WALLETS = {
    'ETH': ['0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765'],
    'USDT': ['0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765'],
    'USDC': ['0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765'],
}
```

### Multiple Wallets (Production):
```python
RESERVE_WALLETS = {
    'ETH': [
        '0xHotWallet123...',   # For daily operations
        '0xColdWallet456...', # For cold storage
    ],
    'USDT': ['0xHotWallet123...'],
    'USDC': ['0xHotWallet123...'],
}
```

### Using MetaMask:
1. Get your MetaMask address: `0xYourMetaMaskAddress`
2. Update config:
```python
RESERVE_WALLETS = {
    'ETH': ['0xYourMetaMaskAddress'],
    'USDT': ['0xYourMetaMaskAddress'],
    'USDC': ['0xYourMetaMaskAddress'],
}
```

## Troubleshooting

### ❌ "Using placeholder address" warning:
- You haven't updated the default address yet
- Edit `backend/reserve_config.py`
- Replace `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb8`

### ❌ "Failed to connect to Ethereum RPC":
- Check your `SEPOLIA_RPC_URL` in `.env`
- Make sure Infura API key is valid
- Try alternative: `ETH_RPC_URL=https://eth-sepolia.public.blastapi.io`

### ❌ "Balance shows 0 but I have funds":
- Make sure you're on the right network (Sepolia testnet)
- Verify address is correct
- Check balance on Etherscan: `https://sepolia.etherscan.io/address/YOUR_ADDRESS`

## Next Steps

After configuration:
1. ✅ Run `python check_wallets.py` to verify
2. ✅ Start backend: `python main.py`
3. ✅ Open frontend and click "Proof of Reserves"
4. ✅ Check that on-chain verification shows correct balances

## Files Reference

- `backend/reserve_config.py` - Main configuration file
- `backend/check_wallets.py` - Utility to check configuration
- `backend/proof_of_reserves.py` - Uses the configuration
- `.env` - Environment variables (optional override)

---

**Need help?** Run `python check_wallets.py` for detailed info!
