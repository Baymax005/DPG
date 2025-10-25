# 🚀 DPG - Decentralized Payment Gateway

**A modern payment gateway bridging traditional finance with cryptocurrency**

![Status](https://img.shields.io/badge/Status-MVP%20Complete-green)
![Version](https://img.shields.io/badge/Version-1.0.0--MVP-blue)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.120.0-009688)

---

## 📖 Table of Contents
- [Overview](#overview)
- [DPG Token](#-dpg-token)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Tokenomics](#tokenomics)
- [License](#license)

---

## 🎯 Overview

DPG is a comprehensive payment gateway that enables users to:
- Manage multiple fiat and cryptocurrency wallets
- Perform deposits, withdrawals, and transfers
- Trade between currencies (planned)
- Access virtual debit cards (planned)
- **Earn rewards with $DPG native token** (planned Q2 2026)

### 🪙 DPG Token
DPG has its own native utility token ($DPG) providing:
- **Fee Discounts:** Up to 80% off trading fees for holders
- **Staking Rewards:** Earn 5-15% APY on staked tokens
- **Governance Rights:** Vote on platform decisions
- **Airdrops:** Early adopters receive token airdrops
- See [TOKENOMICS.md](docs/TOKENOMICS.md) for complete details
- Accept merchant payments (planned)

**Current Status:** ✅ MVP completed with authentication, wallets, and basic transactions.

**See [docs/PROJECT_STATUS.md](./docs/PROJECT_STATUS.md) for detailed progress tracking.**

---

## ✨ Features

### ✅ Implemented (v1.0.0-MVP)

#### User Authentication
- Email/password registration with validation
- Secure JWT token-based login
- Password requirements (8+ chars, uppercase, lowercase, number)
- Protected API routes
- Password visibility toggle

#### Multi-Currency Wallets
- **Fiat:** USD
- **Crypto:** ETH, MATIC, USDT, USDC
- Ethereum wallet generation with Web3.py
- Private key encryption (Fernet)
- Balance tracking
- Wallet creation/deletion

#### Transactions
- **Deposits:** Instant, 0% fee
- **Withdrawals:** 0.5% fee for crypto
- Transaction history with status tracking
- Reference ID support (Stripe integration ready)

#### Frontend UI
- Responsive design (Tailwind CSS)
- Login/Registration with tab switching
- Dashboard with wallet overview
- Create wallet modal
- Deposit/Withdraw modals
- Real-time transaction history
- Form validation & error handling
- Enter key support

### 🚧 In Progress
- [ ] Stress testing
- [ ] Transfer between wallets
- [ ] Email verification
- [ ] Blockchain testnet integration

### 📋 Planned Features
- Stripe payment integration
- KYC verification system
- Cryptocurrency trading
- Virtual debit cards
- Merchant accounts
- Mobile app

**Full roadmap in [docs/PROJECT_STATUS.md](./docs/PROJECT_STATUS.md)**

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI 0.120.0
- **Database:** PostgreSQL 17
- **ORM:** SQLAlchemy
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt 4.0.1
- **Blockchain:** Web3.py 7.14.0, eth-account 0.13.7
- **Encryption:** cryptography 46.0.3 (Fernet)

### Frontend
- **HTML5 + Vanilla JavaScript**
- **CSS:** Tailwind CSS (CDN)
- **Icons:** Font Awesome 6.4.0

### Infrastructure
- **Python:** 3.13.1
- **Virtual Environment:** venv
- **Server:** Uvicorn (ASGI)

---

## 📦 Installation

### Prerequisites
- Python 3.13+
- PostgreSQL 17+

### Quick Start

1. **Clone & Setup:**
```bash
cd "C:\Users\muham\OneDrive\Desktop\OTHER LANGS\DPG"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Configure Database:**
Create database in PostgreSQL:
```sql
CREATE DATABASE dpg_dev;
```

3. **Environment Variables:**
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
# Then edit .env with your actual credentials
```

4. **Start Server:**
```bash
cd backend
python main.py
```
Server runs at: `http://localhost:9000`

5. **Open Frontend:**
- Double-click `frontend/index.html`
- OR use Live Server on port 5500

---

## 🚀 Usage

### Register New Account
1. Open frontend
2. Click "Sign Up" tab
3. Enter:
   - Email
   - Password (8+ chars, 1 upper, 1 lower, 1 number)
   - First Name
   - Last Name

### Create Wallet
1. Login to dashboard
2. Click "Create New Wallet"
3. Select currency (USD, ETH, MATIC, USDT, USDC)
4. Wallet created instantly

### Deposit Funds
1. Click "Deposit Funds"
2. Select wallet
3. Enter amount
4. Submit (instant, 0% fee)

### Withdraw Funds
1. Click "Withdraw Funds"
2. Select wallet
3. Enter amount
4. Submit (0.5% fee for crypto)

### View Transactions
- Click "View Transactions"
- Auto-refreshes after each action
- Shows type, amount, fee, status, date

---

## 📚 API Documentation

### Base URL
```
http://localhost:9000/api/v1
```

### Interactive Docs
**Swagger UI:** `http://localhost:9000/docs`  
**ReDoc:** `http://localhost:9000/redoc`

### Quick Reference

#### Authentication
```bash
# Register
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe"
}

# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
# Returns: { "access_token": "...", "token_type": "bearer" }

# Get Profile
GET /api/v1/auth/me
Authorization: Bearer <token>
```

#### Wallets
```bash
# Create Wallet
POST /api/v1/wallets/create
Authorization: Bearer <token>
{
  "currency_code": "ETH",
  "wallet_type": "crypto"
}

# List Wallets
GET /api/v1/wallets/
Authorization: Bearer <token>

# Get Wallet
GET /api/v1/wallets/{wallet_id}
Authorization: Bearer <token>

# Delete Wallet
DELETE /api/v1/wallets/{wallet_id}
Authorization: Bearer <token>
```

#### Transactions
```bash
# Deposit
POST /api/v1/transactions/deposit
Authorization: Bearer <token>
{
  "wallet_id": "uuid",
  "amount": 1000.00,
  "description": "Initial deposit"
}

# Withdraw
POST /api/v1/transactions/withdraw
Authorization: Bearer <token>
{
  "wallet_id": "uuid",
  "amount": 100.00,
  "description": "Withdrawal"
}

# Transaction History
GET /api/v1/transactions/history?limit=20
Authorization: Bearer <token>

# Wallet Transactions
GET /api/v1/transactions/wallet/{wallet_id}
Authorization: Bearer <token>
```

---

## 📁 Project Structure

```
DPG/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── database.py             # Database connection & session
│   ├── models.py               # SQLAlchemy models (User, Wallet, Transaction)
│   ├── schemas.py              # Pydantic schemas for validation
│   ├── auth_routes.py          # Authentication endpoints
│   ├── auth_utils.py           # Auth utilities (JWT, hashing)
│   ├── wallet_routes.py        # Wallet management endpoints
│   ├── wallet_service.py       # Wallet business logic
│   ├── transaction_routes.py   # Transaction endpoints
│   └── transaction_service.py  # Transaction business logic
│
├── frontend/
│   ├── index.html              # Main UI (login, dashboard, modals)
│   └── app.js                  # Frontend JavaScript (API calls)
│
├── tests/
│   ├── test_register.py        # Registration tests
│   ├── test_wallets.py         # Wallet tests
│   ├── test_complete_system.py # Full system tests
│   └── test_system.ps1         # PowerShell test script
│
├── utils/
│   ├── db_dashboard.py         # Database overview utility
│   └── view_users.py           # User listing utility
│
├── docs/                       # 📚 All Documentation
│   ├── PROJECT_STATUS.md       # ⭐ Detailed progress tracker
│   ├── TODO.md                 # ⭐ Task list & priorities
│   ├── QUICK_REFERENCE.md      # ⭐ Quick commands & tips
│   ├── WORKSPACE_SUMMARY.md    # Workspace organization
│   ├── README_OLD.md           # Original project vision
│   ├── SOLO_DEVELOPER_ROADMAP.md
│   ├── START_TODAY.md
│   ├── TECH_STACK.md
│   └── ... (other docs)
│
├── .vscode/
│   └── settings.json           # VS Code Python settings
│
├── .env                        # Environment variables (DO NOT COMMIT)
├── requirements.txt            # Python dependencies
└── README.md                   # ⭐ This file (main entry point)
```

---

## 🧪 Testing

### Test Scripts

```bash
# Test user registration
python test_register.py

# Test wallet creation
python test_wallets.py

# Test complete system
python test_complete_system.py

# PowerShell test
.\test_system.ps1
```

### Database Utilities

```bash
# View all registered users
python view_users.py

# Database overview (users, wallets, transactions)
python db_dashboard.py
```

---

## 🔐 Security

### Implemented
- ✅ bcrypt password hashing (rounds=12)
- ✅ JWT token authentication
- ✅ Fernet encryption for private keys
- ✅ Environment variables for secrets
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ CORS configuration
- ✅ Pydantic input validation

### Planned
- ⚠️ 2FA (two-factor authentication)
- ⚠️ Rate limiting
- ⚠️ IP whitelisting
- ⚠️ Security audit

---

## 🗺️ Roadmap

### Phase 2: Core Enhancements (Nov 1-8, 2025)
- [ ] Transfer between wallets
- [ ] Email verification (SendGrid)
- [ ] Blockchain testnet integration
- [ ] Stress testing

### Phase 3: Payment Integration (Nov 8-22, 2025)
- [ ] Stripe integration
- [ ] Bank transfers
- [ ] Transaction limits

### Phase 4: Advanced Features (Dec 2025)
- [ ] KYC verification
- [ ] Cryptocurrency trading
- [ ] Admin dashboard

### Phase 5: Premium Features (Q1 2026)
- [ ] Virtual debit cards
- [ ] Merchant accounts
- [ ] Mobile app

**See [docs/PROJECT_STATUS.md](./docs/PROJECT_STATUS.md) for complete timeline.**

---

## 📊 Current Status

**Version:** 1.0.0-MVP  
**Completion:** 35% overall  
**Phase 1 (MVP):** ✅ 100% Complete  

### Database
- **Users:** 2 registered
- **Wallets:** Working (multiple currencies)
- **Transactions:** Fully functional

### Components Status
- ✅ Backend Infrastructure: 100%
- ✅ Authentication: 100%
- ✅ Wallets: 90%
- ✅ Transactions: 70%
- ✅ Frontend: 80%
- ❌ Email: 0%
- ❌ KYC: 0%
- ❌ Trading: 0%

---

## 🐛 Known Issues

### Minor Issues
- Blockchain transactions are simulated (not live)
- No email notifications yet
- Mobile UI needs improvement
- Need loading spinners

**See [docs/PROJECT_STATUS.md](./docs/PROJECT_STATUS.md) for complete list.**

---

## 💰 Budget

**Total Budget:** $0-500  
**Current Expenses:** $0 (all free tools)  

**Planned:**
- Email service: ~$15-20/month
- Hosting: ~$20-50/month
- SSL: Free (Let's Encrypt)

---

## 📞 Contact

**Developer:** Muhammad Ali (@baymax005)  
**Status:** 4th Semester Student  
**Project Type:** Academic/Portfolio  
**Development:** Active  
**GitHub:** https://github.com/baymax005

---

## 🎓 About the Developer

This project is built by **Muhammad Ali (@baymax005)**, a 4th semester Computer Science student passionate about fintech and blockchain technology.

### Development Philosophy
- **AI-Assisted Development:** Leveraging modern AI tools (ChatGPT, GitHub Copilot) as coding partners
- **Learning by Building:** Creating production-ready systems while gaining practical experience
- **Open Source:** Sharing knowledge and code with the community

### Skills Demonstrated
- Backend development with FastAPI
- Database design with PostgreSQL
- Blockchain integration (Web3.py)
- Authentication & security (JWT, encryption)
- RESTful API design
- Frontend development (HTML/JS)

*Note: This project demonstrates that with the right tools and determination, students can build professional-grade applications. AI tools are used as learning accelerators, not replacements for understanding.*

---

## 🪙 Tokenomics

DPG will launch its native utility token **$DPG** in Q2 2026:

**Token Supply:** 1,000,000,000 (1 Billion) $DPG

**Distribution:**
- 30% Community & Airdrops (early adopters rewarded!)
- 20% Development & Operations
- 20% Liquidity & Exchange Listings
- 15% Team (4-year vesting)
- 15% Reserve & Ecosystem

**Utility:**
- 📉 Up to 80% fee discounts
- 💰 Staking rewards (5-15% APY)
- 🗳️ Governance voting rights
- 🎁 Monthly airdrops for active users
- ⭐ Exclusive features & priority support

**Fair Launch:** No pre-sale, no private rounds - everyone starts equal!

📖 **Complete Details:** See [docs/TOKENOMICS.md](docs/TOKENOMICS.md)

---

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Reliable database
- **Web3.py** - Ethereum integration
- **Tailwind CSS** - Beautiful styling
- **Font Awesome** - Icon library

---

## 📄 License

MIT License - Copyright (c) 2025 Muhammad Ali (@baymax005)

See [LICENSE](./LICENSE) file for details.

This project is open source for educational and portfolio purposes. Commercial use is permitted under MIT terms.

---

**Last Updated:** October 26, 2025  
**Built with:** ❤️ + Python + AI Assistance  
**Developer:** Muhammad Ali (@baymax005)  
**Status:** 🟢 Active Development  

**Let's revolutionize payments together! 🚀**
