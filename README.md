# 🚀 DPG - Decentralized Payment Gateway

**A modern payment gateway bridging traditional finance with cryptocurrency**

![Status](https://img.shields.io/badge/Status-Production%20Ready%20(Testnet)-brightgreen)
![Version](https://img.shields.io/badge/Version-0.2.1--Beta-blue)
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

**Current Status:** ✅ Production-ready on testnet! Nonce errors fixed, auto-status updates, precise amount display.

**See [docs/BLOCKCHAIN_SETUP.md](./docs/BLOCKCHAIN_SETUP.md) for blockchain integration guide.**  
**See [docs/PROJECT_STATUS.md](./docs/PROJECT_STATUS.md) for detailed progress tracking.**  
**See [CHANGELOG.md](./CHANGELOG.md) for latest updates (v0.2.1).**

---

## ✨ Features

### ✅ Implemented (v0.2.1 - Production Ready!)

#### User Authentication
- Email/password registration with validation
- Secure JWT token-based login
- Password requirements (8+ chars, uppercase, lowercase, number)
- Protected API routes
- Password visibility toggle

#### Multi-Currency Wallets
- **Fiat:** USD
- **Crypto:** ETH, MATIC, USDT, USDC
- **Import existing wallets** (MetaMask, Trust Wallet, etc.)
- **Real blockchain integration** with Web3.py 7.14.0
- **Enterprise-grade encryption** (PBKDF2 + Fernet)
- **Sync balance from blockchain** (Sepolia testnet)
- Wallet creation/deletion
- Delete empty wallets
- **Precise balance display** (0.001 shows correctly, not 0.00)

#### Blockchain Transactions (NEW v0.2.1 🔥)
- **Real crypto sends** on Sepolia testnet (ETH, MATIC)
- **Fixed nonce errors** (uses 'pending' nonce, no more conflicts)
- **20% gas price buffer** (prevents "underpriced" errors)
- **Rate limiting** (blocks rapid-fire transactions)
- **Auto-status updates** (pending → completed in 10-15 seconds)
- Gas fee estimation before sending
- Transaction hash tracking
- Etherscan verification links
- User's wallet private key signing (not master wallet)
- Address validation (checksum addresses)

#### Transactions
- **Real blockchain sends:** Send ETH/MATIC to any address
- **Transaction monitor** (checks blockchain every 10 seconds)
- **Auto-refresh frontend** (updates every 15 seconds, no manual refresh)
- Transaction history with **precise amounts** (8 decimals for crypto)
- **Details column** (network, tx hash links, descriptions)
- Reference ID support
- Gas fee display
- **Disabled send button** during transaction (prevents double-send)

#### Frontend UI
- Responsive design (Tailwind CSS)
- Login/Registration with tab switching
- Dashboard with wallet overview
- **Import Wallet modal** with security warnings
- Create wallet modal
- Send crypto with address input
- **Sync balance button** (fetch from blockchain)
- Real-time transaction history
- Form validation & error handling
- Enter key support

#### Proof of Reserves (NEW v0.2.2 🔥)
- **Full Transparency:** Public API for verifying platform reserves
- **Merkle Trees:** Cryptographic proof of user balance inclusion
- **On-Chain Verification:** Compare reported reserves with actual blockchain balances
- **Solvency Ratios:** Real-time calculation showing platform is fully reserved (100%+)
- **Currency Breakdown:** Separate reporting for ETH, USDT, USDC, MATIC, USD
- **Audit Dashboard:** Beautiful UI showing reserves, liabilities, and Merkle tree roots
- **Etherscan Links:** Direct verification on blockchain explorers
- **Reserve Wallets:** Configurable via reserve_config.py or environment variables

#### Transaction Receipts (NEW v0.2.2 🔥)
- **Elegant DPG Branding:** Professional purple-blue gradient design
- **Detailed Receipts:** View complete transaction details with QR codes
- **Print/Export:** Print receipts for accounting purposes
- **Blockchain Verification:** Direct links to Etherscan/Polygonscan
- **Status Tracking:** Real-time status with gradient badges (✅ ⏳ ❌)
- **Copy Functionality:** Easy copy-to-clipboard for transaction hashes
- **Premium UI:** Shadows, gradients, icons - professional appearance

### 🚧 In Progress
- [ ] Email verification
- [ ] ERC-20 token on-chain support (currently custodial USDT/USDC)
- [ ] Polygon Mumbai testnet transactions

### 📋 Planned Features
- Mainnet deployment (after security audit)
- Polygon Mumbai testnet support
- Multi-currency swap (DEX integration)
- Stripe payment integration (fiat on-ramp)
- KYC verification system
- Virtual debit cards
- Merchant accounts
- Mobile app

**Full roadmap in [docs/PROJECT_STATUS.md](./docs/PROJECT_STATUS.md)**

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI 0.120.0
- **Database:** PostgreSQL 17 (dpg_user/dpg_payment_gateway)
- **ORM:** SQLAlchemy
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt 4.2.0
- **Blockchain:** Web3.py 7.14.0, eth-account 0.13.7
- **Encryption:** cryptography 46.0.3 (Fernet)
- **RPC Provider:** Infura (Sepolia testnet)
- **Networks:** Ethereum Sepolia, Polygon Mumbai (planned)

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
python -m venv venv_new
.\venv_new\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Configure Database:**
Create PostgreSQL user and database:
```sql
-- As postgres superuser:
CREATE USER dpg_user WITH PASSWORD 'dpg_secure_password_2024';
CREATE DATABASE dpg_payment_gateway OWNER dpg_user;
GRANT ALL PRIVILEGES ON DATABASE dpg_payment_gateway TO dpg_user;
```

3. **Environment Variables:**
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Required `.env` settings:
```env
# Database
DATABASE_URL=postgresql://dpg_user:dpg_secure_password_2024@localhost/dpg_payment_gateway

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Wallet Encryption
WALLET_ENCRYPTION_KEY=your-32-byte-fernet-key-here

# Blockchain (Infura)
INFURA_API_KEY=your-infura-api-key
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/your-infura-api-key
MUMBAI_RPC_URL=https://polygon-mumbai.infura.io/v3/your-infura-api-key
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

**📖 Detailed blockchain setup:** See [docs/BLOCKCHAIN_SETUP.md](./docs/BLOCKCHAIN_SETUP.md)

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

### Import Existing Wallet (NEW! 🔥)
1. Login to dashboard
2. Click "Import Wallet"
3. Select currency (ETH or MATIC)
4. **Enter your private key** (from MetaMask, Trust Wallet, etc.)
5. Wallet imported with real blockchain balance!

**⚠️ Security Note:** Private keys are encrypted with Fernet before storage. NEVER share your private key!

### Create New Wallet
1. Login to dashboard
2. Click "Create New Wallet"
3. Select currency (USD, ETH, MATIC, USDT, USDC)
4. Wallet created with new address (starts with 0 balance)

### Send Crypto (Real Blockchain!)
1. Click "Send Crypto" or click Send on any wallet card
2. Select wallet to send FROM
3. Enter recipient address (any valid Ethereum address)
4. Enter amount (checks for sufficient balance + gas fees)
5. Submit - transaction sent to Sepolia testnet!
6. Get transaction hash and Etherscan link

### Sync Blockchain Balance
1. Find your imported wallet
2. Click "Sync Balance" button
3. Fetches real-time balance from blockchain

### View Transactions
- Click "View Transactions"
- Shows transaction type, amount, fee, status, date
- Includes transaction hashes for blockchain verification

**📖 Complete guide:** See [docs/BLOCKCHAIN_SETUP.md](./docs/BLOCKCHAIN_SETUP.md)

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
# Import Wallet (NEW!)
POST /api/v1/wallets/import
Authorization: Bearer <token>
{
  "currency_code": "ETH",
  "private_key": "0xYourPrivateKeyHere..."
}

# Sync Blockchain Balance
POST /api/v1/wallets/{wallet_id}/sync-blockchain
Authorization: Bearer <token>

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

#### Proof of Reserves (NEW v0.2.2!)
```bash
# Get Complete Reserves Report
GET /api/v1/reserves/report
# Returns: reserves, liabilities, solvency ratios, on-chain comparison

# Get Merkle Tree Root for Currency
GET /api/v1/reserves/merkle/{currency}
# Returns: merkle_root, user_count, total_balance

# Get Solvency Ratios
GET /api/v1/reserves/solvency
# Returns: solvency percentage per currency

# Get On-Chain Reserve Verification
GET /api/v1/reserves/onchain
# Returns: blockchain balances vs reported reserves
```

#### Transactions
```bash
# Send Crypto (Real Blockchain!)
POST /api/v1/transactions/send
Authorization: Bearer <token>
{
  "from_wallet_id": "uuid",
  "to_address": "0xRecipientAddress...",
  "amount": 0.01,
  "description": "Payment"
}
# Returns: { "tx_hash": "0x...", "etherscan_url": "https://sepolia.etherscan.io/tx/0x..." }

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
│   ├── wallet_routes.py        # Wallet management (import, sync, delete)
│   ├── wallet_service.py       # Wallet business logic + encryption
│   ├── transaction_routes.py   # Transaction endpoints (send crypto)
│   ├── transaction_service.py  # Transaction business logic
│   ├── blockchain_service.py   # Web3.py integration (400+ lines)
│   ├── proof_of_reserves.py    # ⭐ NEW: Merkle trees + on-chain verification
│   ├── reserve_config.py       # ⭐ NEW: Reserve wallet configuration
│   └── check_wallets.py        # ⭐ NEW: Utility to check wallet setup
│
├── frontend/
│   ├── index.html              # Main UI (login, dashboard, import modal)
│   └── app.js                  # Frontend JS (import wallet, sync balance)
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
│   ├── BLOCKCHAIN_SETUP.md     # ⭐ Blockchain integration guide
│   ├── PROJECT_STATUS.md       # ⭐ Detailed progress tracker
│   ├── TODO.md                 # ⭐ Task list & priorities
│   ├── QUICK_REFERENCE.md      # ⭐ Quick commands & tips
│   ├── WORKSPACE_SUMMARY.md    # Workspace organization
│   ├── ON_CHAIN_RESERVES.md    # ⭐ NEW: On-chain verification docs
│   ├── RESERVE_WALLET_SETUP.md # ⭐ NEW: Reserve wallet configuration
│   └── TOKENOMICS.md           # Token economics
│
├── .vscode/
│   └── settings.json           # VS Code Python settings
│
├── CHANGELOG.md                # Version history (v0.2.2)
├── DEPLOYMENT.md               # ⭐ NEW: Production deployment guide
├── RESERVE_WALLET_STATUS.md    # ⭐ NEW: Current reserve wallet config
├── .env                        # Environment variables (DO NOT COMMIT)
├── requirements.txt            # Python dependencies (updated)
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

### ✅ Phase 1: MVP (Oct 25-26, 2025) - COMPLETE
- [x] FastAPI backend with PostgreSQL
- [x] JWT authentication
- [x] Multi-currency wallets
- [x] Basic transactions
- [x] Frontend UI

### ✅ Phase 2: Blockchain Integration (Oct 27, 2025) - COMPLETE
- [x] Web3.py integration with Infura
- [x] Import wallet feature
- [x] Real blockchain sends (Sepolia testnet)
- [x] Gas fee estimation
- [x] Transaction hash tracking
- [x] Sync blockchain balance
- [x] Enterprise-grade encryption (PBKDF2)

### ✅ Phase 2.1: Production Polish (Nov 3, 2025) - COMPLETE
- [x] **Fixed nonce errors** (no more "nonce too low")
- [x] **Fixed gas price errors** (20% buffer prevents "underpriced")
- [x] **Transaction monitor** (auto-updates status every 10 seconds)
- [x] **Frontend auto-refresh** (no manual refresh needed)
- [x] **Precise amount display** (8 decimals for crypto)
- [x] **Rate limiting** (prevents rapid-fire transactions)
- [x] **Better error messages** (user-friendly, emoji-enhanced)

### ✅ Phase 2.2: Transparency & Receipts (Nov 5, 2025) - COMPLETE
- [x] **Proof of Reserves** (Merkle tree verification, solvency ratios, on-chain verification)
- [x] **Transaction Receipts** (elegant DPG branding, QR codes, print/export)
- [x] **Public API** (anyone can verify platform reserves)
- [x] **Transparency Dashboard** (beautiful UI for reserves display)
- [x] **Reserve Configuration** (easy wallet management via config file)
- [x] **Production Documentation** (complete deployment guide)

### 🚧 Phase 3: Advanced Features (Nov 4-8, 2025) - IN PROGRESS
- [ ] Export wallet feature (show private key securely)
- [ ] ERC-20 token support (USDT, USDC on-chain)
- [ ] Polygon Mumbai testnet
- [ ] Email verification (SendGrid)
- [ ] UI improvements (loading, animations)

### 📋 Phase 4: Premium Features (Nov 8-22, 2025)
- [ ] Multi-currency swap (DEX integration)
- [ ] Stripe payment integration
- [ ] Bank transfers
- [ ] KYC verification

### 🎯 Phase 5: Production (Dec 2025)
- [ ] Security audit (professional)
- [ ] Mainnet deployment
- [ ] Rate limiting & monitoring
- [ ] Admin dashboard

### 🚀 Phase 6: Scale (Q1 2026)
- [ ] Virtual debit cards
- [ ] Merchant accounts
- [ ] Mobile app (React Native)
- [ ] $DPG token launch

**See [docs/TODO.md](./docs/TODO.md) for detailed task breakdown.**

---

## 📊 Current Status

**Version:** 0.2.2-Beta  
**Major Milestone:** ✅ Transparent & Auditable Platform!  
**Completion:** 60% overall  

### Latest Achievements (Nov 5, 2025) 🔥
- ✅ **Proof of Reserves System** (Merkle trees + on-chain verification + solvency ratios)
- ✅ **Transaction Receipts with DPG Branding** (elegant design, QR codes, print functionality)
- ✅ **Reserve Wallet Configuration** (centralized config file, environment override support)
- ✅ **Production Deployment Guide** (comprehensive DEPLOYMENT.md with security best practices)
- ✅ **Public Transparency API** (anyone can verify reserves on blockchain)
- ✅ **Audit Dashboard** (beautiful UI showing full financial transparency)

### Previous Achievements (Nov 3, 2025)
- ✅ **Fixed all nonce errors** (pending nonce + 20% gas buffer)
- ✅ **Auto-status updates** (monitor checks every 10 seconds)
- ✅ **Frontend auto-refresh** (updates every 15 seconds)
- ✅ **Precise amounts** (0.001 ETH displays correctly)
- ✅ **Rate limiting** (prevents transaction spam)
- ✅ **Enhanced UI** (Details column with tx links)
- ✅ **Better UX** (disabled button during send, no double-clicks)

### Previous Achievements (Oct 27, 2025)
- ✅ Import wallet feature (MetaMask, Trust Wallet)
- ✅ Real blockchain sends (Sepolia testnet)
- ✅ Gas fee estimation
- ✅ Transaction hash tracking
- ✅ Sync blockchain balance
- ✅ Enterprise encryption (PBKDF2 + Fernet)
- ✅ Delete wallet functionality
- ✅ Removed fake deposits/withdrawals

### Database
- **Users:** Active authentication system
- **Wallets:** Import + Create functionality
- **Transactions:** Real blockchain transactions tracked

### Components Status
- ✅ Backend Infrastructure: 100%
- ✅ Authentication: 100%
- ✅ Wallets: 95% (import, sync, delete - export coming soon)
- ✅ Blockchain Integration: 95% (Sepolia production-ready, Mumbai planned)
- ✅ Transactions: 95% (send working, auto-status updates, nonce fixed)
- ✅ Frontend: 90% (auto-refresh working, polish ongoing)
- ⏳ Email: 0% (planned)
- ❌ KYC: 0% (future)
- ❌ Trading: 0% (future)

**📖 Full details:** See [CHANGELOG.md](./CHANGELOG.md) for v0.2.1 release notes.

---

## 🐛 Known Issues

### Priority Fixes Needed
- [ ] Transaction status tracking (Pending → Confirmed)
- [ ] Loading spinners during blockchain operations
- [ ] Mobile UI responsiveness
- [ ] Better error messages for blockchain failures

### Minor Issues
- [ ] bcrypt version warning (harmless)
- [ ] No confirmation modal before delete wallet
- [ ] Transaction history doesn't show Etherscan links yet
- [ ] No favicon.ico

**📝 Full list:** See [docs/TODO.md](./docs/TODO.md) for complete bug tracker.

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

**Last Updated:** November 5, 2025 (v0.2.2 - Fully Transparent & Production-Ready Docs! 🔥)  
**Built with:** ❤️ + Python + Web3.py + Cryptography + AI Assistance  
**Developer:** Muhammad Ali (@baymax005)  
**Status:** 🟢 Active Development - Transparent, Auditable & Deployment-Ready!

**Let's revolutionize payments together! 🚀**
