# 🔐 FIX: Wallet Decryption Error

## Problem
You're getting: `Failed to decrypt wallet key`

This happens because your wallet was encrypted with a **temporary key** that changes every time you restart the backend.

---

## ✅ QUICK FIX (Choose ONE option)

### Option 1: Use the Automatic Fix Script (EASIEST)

```powershell
cd backend
python fix_wallet_key.py
```

Follow the prompts:
- Choose option 1 to generate a NEW key (will need to re-import wallets)
- OR choose option 2 if you have the temporary key from logs

---

### Option 2: Manual Fix (If you see the key in backend console)

**Step 1:** Look at your backend terminal when it starts. You'll see:
```
⚠️  Using temporary key: abc123xyz456...
WALLET_ENCRYPTION_KEY=abc123xyz456def789ghi012jkl345mno678pqr==
```

**Step 2:** Copy the FULL key after `WALLET_ENCRYPTION_KEY=`

**Step 3:** Add it to `backend/.env`:
```properties
WALLET_ENCRYPTION_KEY=abc123xyz456def789ghi012jkl345mno678pqr==
```

**Step 4:** Restart backend:
```powershell
cd backend
python main.py
```

✅ Your wallets will now decrypt!

---

### Option 3: Fresh Start (If you don't have the key)

If you don't have the temporary key, your old wallets cannot be decrypted. You need to:

**Step 1:** Generate a permanent key
```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Step 2:** Add it to `backend/.env`:
```properties
WALLET_ENCRYPTION_KEY=YOUR_KEY_HERE
```

**Step 3:** Delete old wallets from database (they can't be decrypted)

**Step 4:** Re-import your wallets

---

## 🎯 The Root Cause

Every time you restart the backend WITHOUT a `WALLET_ENCRYPTION_KEY` in .env:
1. Backend generates a NEW random key
2. New wallets encrypt with the NEW key
3. Old wallets encrypted with OLD key cannot decrypt ❌

**Solution:** Set ONE permanent key in .env that never changes!

---

## 📋 After Fix - Test Transaction

Once you've fixed the encryption key:

```powershell
# Restart backend
cd backend
python main.py

# Try sending again - use a VALID 42-character address:
# ✅ Good: 0xa7e9a48acd74a9c62f2508c91fc34644dd3a718d
```

---

## 🚨 Important Notes

1. **NEVER lose your `WALLET_ENCRYPTION_KEY`** - Without it, wallets cannot be decrypted
2. **Keep it in .env file** - Don't commit to GitHub (it's in .gitignore)
3. **One key forever** - Once set, don't change it or all wallets become unreadable
4. **Backup the key** - Store it somewhere safe (password manager, secure notes)

---

## ❓ Which Option Should I Choose?

**Have backend running now?**
→ Check console for the temporary key → Use Option 2

**Backend not running / don't see key?**
→ Use Option 1 (auto script) and choose option 1 or 2

**Want to start completely fresh?**
→ Use Option 3 (generate new key, delete old wallets, re-import)

---

**Need help?** Just ask! But first try the automatic fix script - it's the easiest way.
