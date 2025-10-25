# 🚀 DPG - Quick Reference Guide

**Fast access to common commands and information**

---

## ⚡ Quick Commands

### Start Development Server
```bash
cd backend
python main.py
```
Server: http://localhost:9000  
Docs: http://localhost:9000/docs

### Open Frontend
```bash
# Option 1: Double-click
frontend/index.html

# Option 2: Live Server (VS Code)
Right-click index.html → Open with Live Server
```
Frontend: http://localhost:5500 or file://

### Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### View Database
```bash
# All users
python utils/view_users.py

# Database overview
python utils/db_dashboard.py
```

### Run Tests
```bash
# All tests
python tests/test_complete_system.py

# Specific test
python tests/test_register.py
python tests/test_wallets.py
```

---

## 📂 Important Files

### Backend Core
- `backend/main.py` - FastAPI app entry point
- `backend/models.py` - Database models
- `backend/schemas.py` - Request/response validation
- `backend/database.py` - DB connection

### Routes
- `backend/auth_routes.py` - Login, register, profile
- `backend/wallet_routes.py` - Wallet management
- `backend/transaction_routes.py` - Deposits, withdrawals

### Services
- `backend/auth_utils.py` - JWT, password hashing
- `backend/wallet_service.py` - Wallet generation, encryption
- `backend/transaction_service.py` - Transaction logic

### Frontend
- `frontend/index.html` - Main UI
- `frontend/app.js` - JavaScript logic

### Configuration
- `.env` - Environment variables (SECRET!)
- `requirements.txt` - Python dependencies
- `.vscode/settings.json` - VS Code config

### Documentation
- `README.md` - Project overview
- `PROJECT_STATUS.md` - Detailed progress tracker
- `TODO.md` - Task list
- `QUICK_REFERENCE.md` - This file

---

## 🔑 Important URLs

### Local Development
- **Backend API:** http://localhost:9000
- **API Docs (Swagger):** http://localhost:9000/docs
- **API Docs (ReDoc):** http://localhost:9000/redoc
- **Frontend:** http://localhost:5500 (Live Server)

### Database
- **Host:** localhost
- **Port:** 5432
- **Database:** dpg_dev
- **User:** postgres
- **Password:** (see .env file)

---

## 📊 Project Structure

```
DPG/
├── backend/          # FastAPI backend
├── frontend/         # HTML/JS frontend
├── tests/           # Test scripts
├── utils/           # Database utilities
├── venv/            # Python virtual environment
├── .env             # Environment variables
└── *.md             # Documentation
```

---

## 🎯 Current Status

**Phase:** 1 (MVP) - ✅ COMPLETE  
**Version:** 1.0.0-MVP  
**Progress:** 35% overall

### What's Working
- ✅ User authentication
- ✅ Multi-currency wallets
- ✅ Deposits & withdrawals
- ✅ Transaction history
- ✅ Frontend UI

### What's Next
- 🔴 Stress testing
- 🔴 Transfer feature
- 🟡 Email verification

---

## 🐛 Common Issues & Solutions

### Server won't start
```bash
# Check if port 9000 is in use
netstat -ano | findstr :9000

# Kill the process
taskkill /PID <PID> /F

# Restart server
cd backend
python main.py
```

### Database connection error
```bash
# Check PostgreSQL is running
# Windows: Services → PostgreSQL

# Test connection
psql -U postgres -d dpg_dev
```

### Import errors
```bash
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend not connecting to backend
- Check backend is running on port 9000
- Check CORS is enabled in `main.py`
- Check `API_URL` in `app.js` is correct

---

## 📝 Quick Reference Data

### Test Credentials
```
Email: test@example.com
Password: Test123456
```

### Supported Currencies
- **Fiat:** USD
- **Crypto:** ETH, MATIC, USDT, USDC

### Transaction Fees
- **Deposits:** 0%
- **Withdrawals (Crypto):** 0.5%
- **Withdrawals (Fiat):** 0%
- **Transfers:** 0.1%

### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number

---

## 🔐 Security Keys

### Environment Variables
```env
# Copy from .env.example and fill in your actual values
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/dpg_dev
SECRET_KEY=your-jwt-secret-key-min-32-characters
WALLET_ENCRYPTION_KEY=your-fernet-key-generate-new-one
```

⚠️ **NEVER commit .env to GitHub!**

---

## 📞 Quick Contacts

### Database
```bash
# Connect to database
psql -U postgres -d dpg_dev

# List tables
\dt

# Describe table
\d users
\d wallets
\d transactions

# Count users
SELECT COUNT(*) FROM users;
```

### Git Commands
```bash
# Status
git status

# Commit
git add .
git commit -m "Your message"

# Push
git push origin main
```

---

## 🎓 Learning Resources

### FastAPI
- Docs: https://fastapi.tiangolo.com
- Tutorial: https://fastapi.tiangolo.com/tutorial

### SQLAlchemy
- Docs: https://docs.sqlalchemy.org
- ORM Tutorial: https://docs.sqlalchemy.org/en/14/orm/tutorial.html

### Web3.py
- Docs: https://web3py.readthedocs.io
- Examples: https://web3py.readthedocs.io/en/stable/examples.html

### PostgreSQL
- Docs: https://www.postgresql.org/docs
- Tutorial: https://www.postgresqltutorial.com

---

## ⚡ Productivity Tips

### VS Code Extensions
- Python (Microsoft)
- Pylance
- SQLTools
- Thunder Client (API testing)
- Live Server

### Keyboard Shortcuts
- `Ctrl + Shift + P` - Command palette
- `Ctrl + ` ` - Toggle terminal
- `Ctrl + B` - Toggle sidebar
- `F5` - Debug

### Time Savers
```bash
# Create alias for server start
# Add to PowerShell profile:
function Start-DPG { cd backend; python main.py }

# Then just run:
Start-DPG
```

---

## 📊 Progress Tracking

### Daily Checklist
- [ ] Check server is running
- [ ] Review errors in terminal
- [ ] Test one feature
- [ ] Update TODO.md
- [ ] Commit changes

### Weekly Goals
See `TODO.md` for detailed tasks.

### Monthly Milestones
See `PROJECT_STATUS.md` for timeline.

---

**Last Updated:** October 25, 2025  
**Quick Help:** Check README.md or PROJECT_STATUS.md for details
