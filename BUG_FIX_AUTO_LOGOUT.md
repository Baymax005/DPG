# 🐛 Auto-Logout Bug Fix - Complete Solution

**Date:** November 13, 2025  
**Issue:** Server keeps refreshing and logging users out  
**Status:** ✅ FIXED

---

## 🔍 Root Causes Identified

### 1. **Server Auto-Reload** (PRIMARY ISSUE) 🔴
**Location:** `backend/main.py` line 135  
**Problem:** `uvicorn.run(..., reload=True)` restarts server on ANY file save  
**Impact:** Every file save = server restart = all users logged out  

**Why it happens:**
- Uvicorn watches for file changes
- Auto-reloads to apply code updates
- Kills all active sessions/connections
- JWT tokens become invalid on restart

### 2. **Token Expiration Too Short** ⏰
**Location:** `backend/auth_routes.py` line 19  
**Problem:** JWT tokens expire after only 30 minutes  
**Impact:** Users logged out every 30 minutes even if server stable  

**Why it's problematic:**
- Too short for development/testing
- Annoying user experience
- No token refresh mechanism implemented

### 3. **Aggressive Error Handling** ⚠️
**Location:** `frontend/app.js` lines 287, 291  
**Problem:** `logout()` called on ANY error, including network issues  
**Impact:** Temporary network hiccup = full logout  

**What triggers it:**
- Server temporarily down
- Slow network connection
- API timeout
- ANY fetch error

### 4. **No Token Refresh** 🔄
**Problem:** No mechanism to refresh tokens before expiration  
**Impact:** Token expires = hard logout, lose all work  

---

## ✅ Solutions Implemented

### 1. **Conditional Auto-Reload** ✅
**File:** `backend/main.py`

```python
# OLD CODE (causes constant restarts):
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=9000,
    reload=True,  # ❌ Always on
    log_level="info"
)

# NEW CODE (smart reload):
is_production = os.getenv("NODE_ENV", "development") == "production"

uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=9000,
    reload=not is_production,  # ✅ Only in dev mode
    log_level="info"
)
```

**Benefits:**
- ✅ Set `NODE_ENV=production` = no auto-reload = stable sessions
- ✅ Set `NODE_ENV=development` = auto-reload = quick iteration
- ✅ Default to development for convenience

### 2. **Extended Token Expiration** ✅
**File:** `backend/auth_routes.py`

```python
# OLD CODE:
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # ❌ Too short

# NEW CODE:
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # ✅ 24 hours
```

**Benefits:**
- ✅ 24-hour token life by default
- ✅ Configurable via environment variable
- ✅ Better development experience
- ⚠️ Note: In production, use shorter time + refresh tokens

### 3. **Smart Error Handling** ✅
**File:** `frontend/app.js`

```javascript
// OLD CODE (logout on any error):
if (userResponse.ok) {
    // success
} else {
    logout();  // ❌ Too aggressive
}

// NEW CODE (only logout on 401):
if (userResponse.ok) {
    // success
} else if (userResponse.status === 401) {
    console.warn('⚠️ Session expired or invalid token');
    logout();  // ✅ Only on auth failure
} else {
    console.error('❌ Error loading dashboard:', userResponse.status);
    alert('Unable to load dashboard. Please try refreshing the page.');
    // ✅ Don't logout on other errors
}
```

**Benefits:**
- ✅ Only logout on 401 Unauthorized
- ✅ Network errors don't force logout
- ✅ Better user experience
- ✅ Less data loss

### 4. **API Fetch Wrapper** ✅
**File:** `frontend/app.js`

Added new helper function:
```javascript
async function apiFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        // Auto-logout only on 401 Unauthorized
        if (response.status === 401) {
            console.warn('⚠️ Session expired (401) - logging out');
            logout();
            throw new Error('Session expired. Please login again.');
        }
        
        return response;
    } catch (error) {
        // Don't logout on network errors
        if (error.message.includes('Session expired')) {
            throw error;
        }
        console.error('❌ API Error:', error);
        throw error;
    }
}
```

**Benefits:**
- ✅ Centralized 401 handling
- ✅ Consistent behavior across all API calls
- ✅ Easy to maintain

---

## 🚀 New Startup Scripts

Created two PowerShell scripts for different needs:

### **start_stable.ps1** - Recommended for Testing
```powershell
# Sets NODE_ENV=production
# Disables auto-reload
# Stable sessions
# Use when testing features
```

**Run with:**
```powershell
cd backend
.\start_stable.ps1
```

### **start_dev.ps1** - For Active Development
```powershell
# Sets NODE_ENV=development
# Enables auto-reload
# Quick code updates
# Use when writing code
```

**Run with:**
```powershell
cd backend
.\start_dev.ps1
```

---

## 📋 How to Use

### For Stable Testing (Recommended):
1. Open PowerShell in `backend/` folder
2. Run: `.\start_stable.ps1`
3. Server won't restart on file changes
4. Sessions remain stable
5. Token valid for 24 hours
6. No more random logouts! 🎉

### For Active Development:
1. Open PowerShell in `backend/` folder
2. Run: `.\start_dev.ps1`
3. Server auto-reloads on file changes
4. Quick iteration
5. ⚠️ May log users out on restart

### Manual Control:
```powershell
# Stable mode
$env:NODE_ENV = "production"
python main.py

# Dev mode
$env:NODE_ENV = "development"
python main.py
```

---

## 🧪 Testing the Fix

### Test 1: Stable Sessions
1. Start server with `start_stable.ps1`
2. Login to frontend
3. Make code changes and save files
4. **Expected:** User stays logged in ✅
5. **Before:** User logged out ❌

### Test 2: Long Sessions
1. Login to dashboard
2. Leave tab open for 1+ hours
3. **Expected:** Still logged in (24h token) ✅
4. **Before:** Logged out after 30 mins ❌

### Test 3: Network Errors
1. Login to dashboard
2. Stop backend server temporarily
3. Try to load wallets
4. **Expected:** Error message, but stay logged in ✅
5. **Before:** Instant logout ❌

### Test 4: Token Expiration
1. Login to dashboard
2. Wait 24+ hours (or change token expiry to 1 min for testing)
3. Try to access protected resource
4. **Expected:** Clean 401 error + logout ✅
5. **Before:** Same, but happened every 30 mins ❌

---

## ⚙️ Configuration Options

### Environment Variables (.env)

```bash
# Server mode
NODE_ENV=production  # stable sessions
# NODE_ENV=development  # auto-reload

# Token expiration (in minutes)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours (default)
# JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30  # 30 minutes (production)
# JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days (testing)
```

### Recommended Settings

**Development (Writing Code):**
```bash
NODE_ENV=development
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

**Testing (Stable Sessions):**
```bash
NODE_ENV=production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

**Production (Real Users):**
```bash
NODE_ENV=production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60  # 1 hour + implement refresh tokens
```

---

## 🔒 Security Notes

### Token Expiration
- ✅ 24 hours is fine for development/testing
- ⚠️ For production, use shorter expiration (30-60 min)
- 🔄 Implement refresh token mechanism for production
- 🔐 Always use HTTPS in production

### Auto-Reload
- ✅ Safe in development (controlled environment)
- ⚠️ Never use in production (causes downtime)
- 🔄 Use proper deployment with zero-downtime updates

---

## 📊 Before vs After

| Issue | Before | After |
|-------|--------|-------|
| File save | Logs out users ❌ | No logout ✅ |
| Token life | 30 minutes ❌ | 24 hours ✅ |
| Network error | Logs out ❌ | Shows error ✅ |
| Development | Unstable ❌ | Stable ✅ |
| User experience | Frustrating ❌ | Smooth ✅ |

---

## 🎯 Next Steps (Future Improvements)

### 1. Refresh Token System
- Implement refresh tokens for production
- Auto-refresh before expiration
- Seamless user experience

### 2. Token Storage
- Consider using HttpOnly cookies
- More secure than localStorage
- Prevents XSS attacks

### 3. Session Management
- Track active sessions
- Allow logout from all devices
- Session activity monitoring

### 4. Rate Limiting
- Prevent brute force attacks
- Limit login attempts
- IP-based throttling

---

## 🐛 If Issues Persist

### Problem: Still Getting Logged Out
1. Check server isn't restarting:
   ```powershell
   # Look for "Started reloader process" in logs
   # If present, auto-reload is still on
   ```

2. Verify environment variable:
   ```powershell
   echo $env:NODE_ENV
   # Should show "production" for stable mode
   ```

3. Check token expiration:
   ```python
   # In auth_routes.py, verify:
   ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # Should be 1440
   ```

4. Clear browser cache:
   - Old tokens might be cached
   - Clear localStorage
   - Login again

### Problem: Auto-Reload Not Working
1. Make sure using `start_dev.ps1`
2. Verify `NODE_ENV=development`
3. Check uvicorn logs for "reload" message

### Problem: Still Getting 401 Errors
1. Check JWT secret key is consistent
2. Verify SECRET_KEY in .env matches
3. Token might be from old server instance
4. Try logging out and back in

---

## 📁 Files Modified

1. ✅ `backend/main.py` - Conditional auto-reload
2. ✅ `backend/auth_routes.py` - Extended token expiration
3. ✅ `frontend/app.js` - Smart error handling + API wrapper
4. ✅ `backend/start_stable.ps1` - NEW: Stable mode script
5. ✅ `backend/start_dev.ps1` - NEW: Dev mode script

---

## 🎉 Summary

**Bug Fixed:** ✅ Server auto-reload causing constant logouts  
**Solution:** Conditional reload based on NODE_ENV  
**Bonus Fixes:** 
- ✅ Extended token life (24 hours)
- ✅ Smart error handling (no logout on network errors)
- ✅ Easy startup scripts (stable vs dev mode)

**Result:** 
- 🎯 Stable development sessions
- 🚀 Better user experience
- 💻 Flexible development workflow
- 🔒 Maintained security

---

**Now you can code without getting logged out every 5 seconds! 🎉**

Use `start_stable.ps1` for testing and `start_dev.ps1` when actively coding.
