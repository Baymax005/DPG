# Changelog

All notable changes to DPG Payment Gateway will be documented in this file.

## [0.2.0] - 2025-10-27

### 🎉 Major Release: Real Blockchain Integration

### Added
- **Import Wallet Feature** - Users can now import existing MetaMask/Trust Wallet by private key
- **Real Blockchain Transactions** - Send actual testnet ETH on Sepolia network
- **Sync Balance Button** - Fetch real-time balance from blockchain
- **Delete Wallet** - Remove wallets with zero balance
- **Blockchain Service** (`blockchain_service.py`) - Full Web3.py integration with Infura
- **Network Support** - Sepolia testnet, Ethereum mainnet, Mumbai, Polygon
- **Gas Fee Estimation** - Accurate gas cost calculation before sending
- **Transaction Hash Tracking** - Store and display tx_hash for Etherscan verification
- **Encrypted Private Key Storage** - Fernet encryption for wallet security

### Changed
- **Removed Fake Deposits** - No more simulation, only real blockchain operations
- **Removed Fake Withdrawals** - Cleaned up mock transaction system
- **Updated `/send` Endpoint** - Now uses user's wallet private key instead of master wallet
- **Balance Validation** - Check real blockchain balance before sending
- **Transfer UI** - Now only shows "Send Crypto" (removed fake deposit/withdraw buttons)
- **Wallet Display** - Shows blockchain address with copy-friendly format

### Fixed
- **API URL Routing** - Fixed 404 errors for sync and delete endpoints (added `/api/v1` prefix)
- **Private Key Validation** - Proper format checking (0x + 64 hex characters)
- **Bcrypt Compatibility** - Downgraded to bcrypt 4.2.0 for passlib compatibility
- **PostgreSQL Setup** - Created dpg_user and dpg_payment_gateway database
- **Virtual Environment** - Fixed corrupted venv, created fresh venv_new with all dependencies
- **Balance Display** - Shows 4 decimal places for better precision

### Security
- Private keys encrypted with Fernet before database storage
- Never expose private keys in API responses
- Environment variables for sensitive data (Infura key, database password)
- JWT authentication for all API endpoints
- Testnet-only operations (no real money at risk)

### Technical Details
- **Backend**: FastAPI + SQLAlchemy + Web3.py 7.14.0 + PostgreSQL
- **Frontend**: Vanilla JavaScript + Tailwind CSS
- **Blockchain**: Infura RPC provider + Sepolia testnet
- **Encryption**: Fernet (symmetric encryption) for private keys
- **Database**: PostgreSQL with encrypted wallet columns

### Dependencies Added
- web3==7.14.0
- eth-account==0.13.7
- python-dotenv==1.2.1
- bcrypt==4.2.0 (downgraded from 5.0.0)
- email-validator==2.3.0

### Documentation
- Updated `docs/BLOCKCHAIN_SETUP.md` with import wallet instructions
- Added step-by-step testing guide
- Documented API endpoints for import/sync/send
- Added troubleshooting section

### Known Issues
- bcrypt version warning (harmless, doesn't affect functionality)
- Wallet encryption key warning (using temporary key, needs permanent key in .env)
- Delete button shows even when balance is not exactly 0 (fixed with proper decimal comparison)

---

## [0.1.0] - 2025-10-26

### Initial Release

### Added
- User authentication (register, login, JWT tokens)
- Wallet creation (USD, ETH, MATIC, USDT, USDC)
- Mock deposits and withdrawals (fake money for testing UI)
- Internal transfers between own wallets
- Transaction history
- Dashboard with wallet overview
- PostgreSQL database integration
- FastAPI backend with SQLAlchemy ORM
- Responsive frontend with Tailwind CSS

### Features
- Multi-currency wallet support
- Transaction tracking
- Balance management
- User profile management

---

## Upcoming Features

### [0.3.0] - Planned for Oct 28-29
- Professional UI redesign with charts
- Real-time crypto price tracking
- QR code generation for wallet addresses
- Transaction status notifications
- Better error handling and loading states

### [0.4.0] - Planned for Oct 30 - Nov 2
- ERC-20 token support (USDT, USDC on Ethereum)
- Multi-currency swaps
- Recurring payment automation
- Invoice generation and payment links
- Webhook notifications

### [1.0.0] - Planned for Nov 3-7
- Mainnet deployment (REAL money)
- Security audit and penetration testing
- Rate limiting and DDoS protection
- Customer support system
- Production monitoring and logging
- Mobile responsive optimization

---

**Current Version:** 0.2.0  
**Status:** Beta - Testnet Only  
**Next Release:** October 28, 2025
