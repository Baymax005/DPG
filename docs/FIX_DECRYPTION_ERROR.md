# 🔧 Fix Wallet Decryption Error - Two Solutions

## Problem
Your wallet was encrypted with the **old temporary key**, but the backend is now using the **new enterprise encryption system**.

---

## ✅ **OPTION 1: Re-import Your Wallet** (RECOMMENDED)

If you have your wallet's private key, this is the fastest solution:

### Step 1: Run Re-import Tool
```powershell
cd backend
python reimport_wallet.py
```

### Step 2: Enter Your Private Key
When prompted, enter your wallet's private key (starts with `0x`)

### Step 3: Restart Backend
```powershell
python main.py
```

### Step 4: Test Transaction
Your transaction should now work! ✅

---

## ✅ **OPTION 2: Create a New Wallet**

If you don't have the private key, create a fresh wallet:

### Step 1: Delete Old Wallet (via API or Database)

**Via API:**
```powershell
# Get your JWT token
$token = "your-jwt-token"

# Delete wallet
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/wallets/your-wallet-id" `
    -Method DELETE `
    -Headers @{ "Authorization" = "Bearer $token" }
```

**Or via Database:**
```powershell
# Connect to PostgreSQL and delete the wallet
psql -U dpg_user -d dpg_payment_gateway
DELETE FROM wallets WHERE id = 'your-wallet-id';
```

### Step 2: Create New Wallet

Through your frontend application or API:
```powershell
# Create new ETH wallet
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/wallets/create" `
    -Method POST `
    -Headers @{ "Authorization" = "Bearer $token" } `
    -ContentType "application/json" `
    -Body '{"currency_code": "ETH"}'
```

The new wallet will be encrypted with the enterprise system automatically! ✅

---

## 🚨 **Which Option Should You Choose?**

### Choose **Option 1** if:
- ✅ You have the private key
- ✅ The wallet has funds
- ✅ You want to keep the same address

### Choose **Option 2** if:
- ✅ You don't have the private key
- ✅ The wallet is for testing (no real funds)
- ✅ You're okay with a new address

---

## 📋 **Quick Reference**

### Get Your Wallet Address
Check your frontend or run:
```powershell
cd backend
python -c "from database import SessionLocal; from models import Wallet; db = SessionLocal(); wallets = db.query(Wallet).all(); [print(f'{w.currency_code}: {w.address}') for w in wallets]; db.close()"
```

### Check If You Have Private Key
If you created the wallet through the application, the private key was:
- ✅ **Stored encrypted** in database (need old encryption key to decrypt)
- ❌ **Not shown to user** (security best practice)

For production wallets, users should:
- Export and save their private key
- Or use seed phrases (future feature)

---

## 💡 **For Future: Prevent This Issue**

To avoid this in production:

1. **Always backup master key** before changing it
2. **Run migration script** when updating encryption
3. **Give users their private keys** during wallet creation
4. **Implement seed phrases** for wallet recovery

---

**Choose your option and follow the steps above! 🚀**
