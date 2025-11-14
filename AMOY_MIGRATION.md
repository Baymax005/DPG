# Mumbai → Amoy Testnet Migration Guide

**Date**: November 14, 2025  
**Status**: ✅ COMPLETED  
**Commit**: `c911dd6`

## 🚨 What Changed?

Polygon **deprecated Mumbai testnet** (Chain ID 80001) and replaced it with **Amoy testnet** (Chain ID 80002).

All MATIC transactions now use Amoy instead of Mumbai.

---

## ⚡ Quick Migration Steps

### 1. Update Your `.env` File

**Remove this line:**
```env
MUMBAI_RPC_URL=https://polygon-mumbai.infura.io/v3/YOUR_KEY
```

**Add this line:**
```env
AMOY_RPC_URL=https://polygon-amoy.infura.io/v3/YOUR_KEY
```

> **Note:** You can use the same Infura API key! Just change the network from `polygon-mumbai` to `polygon-amoy`.

### 2. Update Infura Project (Optional)

If you're using Infura:
1. Go to https://infura.io/dashboard
2. Select your project
3. Enable **Polygon Amoy** network
4. Mumbai will automatically redirect to Amoy

### 3. Restart Your Server

```bash
cd backend
python main.py
```

That's it! ✅

---

## 📊 What Got Updated?

### Backend Files:
- ✅ `blockchain_service.py` - Network config updated to Amoy (80002)
- ✅ `transaction_scanner.py` - RPC URL changed to Amoy
- ✅ `transaction_routes.py` - Network mapping updated

### Frontend Files:
- ✅ `app.js` - NETWORKS config, explorer URLs updated
- ✅ `index.html` - Dropdown now shows "Amoy Testnet"

### Documentation:
- ✅ `README.md` - All references updated
- ✅ `BLOCKCHAIN_FIXES.md` - Deprecation notice added

---

## 🔗 New URLs

| Item | Old (Mumbai) | New (Amoy) |
|------|-------------|-----------|
| **Chain ID** | 80001 | **80002** |
| **RPC URL** | polygon-mumbai.infura.io | **polygon-amoy.infura.io** |
| **Explorer** | mumbai.polygonscan.com | **amoy.polygonscan.com** |
| **Faucet** | mumbaifaucet.com | **faucet.polygon.technology** |

---

## 🧪 Testing Checklist

After migration, test these features:

### 1. Network Switcher
- [ ] Go to Dashboard
- [ ] Click network dropdown
- [ ] Should see "🟣 Amoy Testnet (MATIC)"
- [ ] Switch to Amoy
- [ ] Network info banner should update

### 2. Create MATIC Wallet
- [ ] Click "Create New Wallet"
- [ ] Select MATIC
- [ ] Wallet should be created successfully
- [ ] Should show "Active Network" badge if Amoy is selected

### 3. Import MATIC Wallet
- [ ] Click "Import Wallet"
- [ ] Select "MATIC (Polygon - Amoy Testnet)"
- [ ] Import with private key
- [ ] Should import successfully

### 4. Get Testnet MATIC
- [ ] Go to https://faucet.polygon.technology/
- [ ] Select "Polygon Amoy"
- [ ] Enter your DPG wallet address
- [ ] Request tokens
- [ ] Wait for confirmation (~5-10 seconds)

### 5. Scan for Deposits
- [ ] Click "📥 Scan Deposits" on MATIC wallet
- [ ] Should scan Amoy blockchain
- [ ] Should detect the faucet deposit
- [ ] Balance should update

### 6. Send MATIC Transaction
- [ ] Click "Transfer" on MATIC wallet
- [ ] Send to another address
- [ ] Network should default to Amoy
- [ ] Transaction should be sent successfully

### 7. Transaction Receipt
- [ ] Go to Transaction History
- [ ] Click "Receipt" on a MATIC transaction
- [ ] Click "View on Polygonscan"
- [ ] Should open **amoy.polygonscan.com** (not Mumbai!)
- [ ] Transaction should be visible on explorer

### 8. Sync Balance
- [ ] Click "🔄 Sync" on MATIC wallet
- [ ] Should sync from Amoy blockchain
- [ ] Balance should match blockchain state

---

## 🆘 Troubleshooting

### Issue: "Failed to connect to network"
**Solution**: 
1. Check your `AMOY_RPC_URL` in `.env`
2. Make sure Infura project has Amoy enabled
3. Verify API key is correct
4. Restart server

### Issue: "No deposits found" when scanning
**Solution**:
1. Make sure you sent MATIC to Amoy testnet (not Mumbai!)
2. Check transaction on https://amoy.polygonscan.com
3. Wait for confirmations (5-10 seconds)
4. Try scanning again

### Issue: Explorer opens but shows "Not Found"
**Solution**:
1. Your transaction might be on old Mumbai testnet
2. Check transaction hash on mumbai.polygonscan.com
3. For new transactions, use amoy.polygonscan.com
4. Old Mumbai transactions cannot be migrated

### Issue: Faucet not working
**Solution**:
1. Use official Polygon faucet: https://faucet.polygon.technology/
2. Select "Polygon Amoy" network
3. You can also try Alchemy: https://www.alchemy.com/faucets/polygon-amoy
4. Wait 24 hours between faucet requests

---

## ⚠️ Important Notes

### Old Mumbai Wallets
- ✅ Your wallet addresses are the **same** (compatible with any EVM chain)
- ✅ You can use the same private key on Amoy
- ⚠️ **BUT**: Any MATIC balance on Mumbai testnet **cannot be transferred to Amoy**
- 💡 **Solution**: Use faucet to get fresh Amoy testnet MATIC

### Transaction History
- Old Mumbai transactions will still show in history
- They will have `network: "mumbai"` (historical data)
- Explorer links for old transactions may not work (Mumbai is deprecated)
- New transactions will use `network: "amoy"`

### Environment Variables
- Keep old `.env` file as backup
- Only change `MUMBAI_RPC_URL` → `AMOY_RPC_URL`
- All other variables remain the same
- Server will ignore missing `MUMBAI_RPC_URL`

---

## 📝 Summary

✅ **Migration completed**: All code updated to Amoy testnet  
✅ **Chain ID**: 80001 → 80002  
✅ **RPC URL**: polygon-amoy.infura.io  
✅ **Explorer**: amoy.polygonscan.com  
✅ **Faucet**: faucet.polygon.technology  
✅ **Commit**: `c911dd6` pushed to GitHub  

**Next Steps:**
1. Update your `.env` file with `AMOY_RPC_URL`
2. Restart your server
3. Test the checklist above
4. Get fresh MATIC from Amoy faucet

---

## 🔗 Useful Links

- **Amoy Faucet**: https://faucet.polygon.technology/
- **Amoy Explorer**: https://amoy.polygonscan.com/
- **Amoy Chainlist**: https://chainlist.org/chain/80002
- **Polygon Docs**: https://docs.polygon.technology/
- **Infura Dashboard**: https://infura.io/dashboard

---

**Migration Status**: ✅ **COMPLETE**  
**System Ready**: ✅ **YES**  
**Action Required**: Update `.env` file only!
