# 🔗 On-Chain Reserve Tracking

## Overview
The DPG platform now includes **on-chain reserve verification** that allows anyone to verify that the platform's database balances match actual blockchain holdings.

## How It Works

### 1. Reserve Wallet Tracking
The platform tracks specific wallet addresses that hold the platform's reserves:

```python
RESERVE_WALLETS = {
    'ETH': ['0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb8'],
    'USDT': ['0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb8'],
    'USDC': ['0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb8'],
}
```

### 2. On-Chain Balance Verification
The `OnChainReserveTracker` class uses Web3.py to:
- Connect to Ethereum via RPC (Sepolia testnet)
- Query ETH balance using `web3.eth.get_balance()`
- Query ERC-20 token balances using contract `balanceOf()` calls
- Compare on-chain totals with database totals

### 3. Public API Endpoints

#### GET /api/v1/reserves/report?include_onchain=true
Complete proof of reserves with on-chain verification:
```json
{
  "reserves": { "ETH": "10.5", "USDT": "25000" },
  "liabilities": { "ETH": "10.5", "USDT": "25000" },
  "solvency": { "ETH": { "ratio_percent": "100.00" } },
  "onchain_verification": {
    "enabled": true,
    "network": "Sepolia Testnet",
    "comparison": {
      "ETH": {
        "database_balance": "10.5",
        "onchain_balance": "10.5",
        "difference": "0.0",
        "match_percent": "100.00",
        "status": "VERIFIED",
        "reserve_wallets": ["0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb8"]
      }
    }
  }
}
```

#### GET /api/v1/reserves/onchain
Dedicated endpoint for blockchain verification only:
```json
{
  "network": "Sepolia Testnet",
  "verified_at": "2025-11-05T10:30:00Z",
  "comparison": {
    "ETH": {
      "database_balance": "10.5",
      "onchain_balance": "10.5",
      "status": "VERIFIED",
      "reserve_wallets": ["0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb8"],
      "explorer_links": [
        "https://sepolia.etherscan.io/address/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb8"
      ]
    }
  }
}
```

## Frontend Display

The Proof of Reserves dashboard now shows:

### On-Chain Verification Section
- ✅ **Blockchain Verified** badge
- Network information (Sepolia Testnet)
- Verification timestamp
- Per-currency comparison cards showing:
  - Database balance
  - On-chain balance
  - Match percentage
  - Verification status (VERIFIED/MISMATCH)
  - Reserve wallet addresses (clickable Etherscan links)

### Visual Indicators
- 🟢 Green cards for VERIFIED matches (≥99.9% match)
- 🟡 Yellow cards for MISMATCH (needs investigation)
- Direct links to Etherscan for independent verification

## Technical Implementation

### Backend Components

#### `OnChainReserveTracker` Class
Located in `backend/proof_of_reserves.py`:

**Key Methods:**
- `__init__()` - Initializes Web3 connection using `ETH_RPC_URL` or `SEPOLIA_RPC_URL`
- `get_eth_balance(address)` - Fetches ETH balance from blockchain
- `get_token_balance(address, token)` - Fetches ERC-20 token balance
- `get_total_reserves(currency)` - Sums balances across all reserve wallets
- `verify_all_reserves()` - Returns complete on-chain verification data

**ERC-20 Integration:**
- Uses minimal ABI with `balanceOf()` and `decimals()` functions
- Supports USDT (6 decimals) and USDC (6 decimals)
- Testnet contracts on Sepolia:
  - USDT: `0x7169D38820dfd117C3FA1f22a697dBA58d90BA06`
  - USDC: `0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8`

#### Updated `ProofOfReservesService`
Enhanced `get_proof_of_reserves_report()` method:
- New parameter: `include_onchain` (default: True)
- Automatically calls `OnChainReserveTracker` if enabled
- Compares database vs blockchain balances
- Calculates match percentage with 0.1% tolerance
- Returns VERIFIED status if difference < 0.001

### Frontend Components

#### `displayProofOfReserves()` Function
Located in `frontend/app.js`:

**New Rendering:**
- Checks for `data.onchain_verification` presence
- Renders green verification banner if enabled
- Creates comparison cards for each currency
- Displays reserve wallet addresses with Etherscan links
- Shows match percentages and verification status

## Security & Transparency

### Why This Matters
1. **Full Transparency:** Anyone can verify reserves without trusting the platform
2. **Cryptographic Proof:** Blockchain provides immutable evidence
3. **Real-Time Verification:** Updates automatically with each API call
4. **Public Auditing:** No authentication required for verification endpoints

### Verification Process
Users can independently verify by:
1. Viewing reserve wallet addresses in the dashboard
2. Clicking Etherscan links to see current balances
3. Comparing with platform's claimed reserves
4. Verifying Merkle tree roots for their own balance inclusion

### Reserve Wallet Security
- Private keys stored securely (not in database)
- Multi-signature wallets recommended for production
- Hardware wallet integration for cold storage
- Regular audits and reconciliation

## Configuration

### Environment Variables
Add to `.env`:
```bash
# Primary RPC URL (used by OnChainReserveTracker)
ETH_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY

# Alternative variable names (fallback)
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
AMOY_RPC_URL=https://polygon-amoy.infura.io/v3/YOUR_INFURA_KEY
```

### Reserve Wallets
Update `RESERVE_WALLETS` in `proof_of_reserves.py` to match your actual reserve addresses:
```python
RESERVE_WALLETS = {
    'ETH': ['0xYourMainReserveWallet', '0xYourColdWallet'],
    'USDT': ['0xYourMainReserveWallet'],
    'USDC': ['0xYourMainReserveWallet'],
}
```

### ERC-20 Token Contracts
Update `TESTNET_TOKENS` for different networks:
```python
# For Mainnet:
MAINNET_TOKENS = {
    'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
}
```

## Production Deployment

### Pre-Launch Checklist
- [ ] Replace testnet RPC URLs with mainnet
- [ ] Update reserve wallet addresses to actual mainnet addresses
- [ ] Update ERC-20 contract addresses to mainnet versions
- [ ] Configure multi-signature wallets for reserves
- [ ] Set up monitoring for balance mismatches
- [ ] Enable alerts if verification fails
- [ ] Test API endpoints thoroughly
- [ ] Perform security audit of reserve wallet access

### Monitoring
Recommended monitoring:
- Track `onchain_verification.comparison[*].status` for MISMATCH
- Alert if `match_percent` falls below 99%
- Log all verification checks for audit trail
- Monitor RPC connection health
- Set up backup RPC providers

### Performance Considerations
- On-chain verification adds ~2-5 seconds to API response
- Use `include_onchain=false` for faster responses
- Consider caching on-chain results (5-10 minute TTL)
- Use WebSocket RPC for faster queries
- Implement rate limiting to avoid RPC quotas

## Testing

### Manual Testing
```bash
# Test ETH balance query
curl "http://localhost:8000/api/v1/reserves/onchain"

# Test full report with on-chain verification
curl "http://localhost:8000/api/v1/reserves/report?include_onchain=true"

# Test without on-chain (faster)
curl "http://localhost:8000/api/v1/reserves/report?include_onchain=false"
```

### Expected Results
- Status: VERIFIED when balances match
- Match percentage: ≥99.9%
- Response time: < 10 seconds
- No errors in console logs

## Future Enhancements

### Planned Features
- [ ] Support for more ERC-20 tokens (DAI, WETH, etc.)
- [ ] Multi-chain support (Polygon, BSC, Arbitrum)
- [ ] Historical tracking of reserve changes
- [ ] Automated alerts for mismatches
- [ ] Proof generation for individual user balances
- [ ] Integration with hardware wallets
- [ ] Real-time WebSocket updates
- [ ] Reserve wallet rotation mechanism

### Advanced Features
- [ ] Multi-signature verification
- [ ] Time-locked reserves
- [ ] Insurance fund tracking
- [ ] Cross-chain reserve aggregation
- [ ] Decentralized oracle integration
- [ ] Zero-knowledge proofs for privacy

## FAQ

**Q: Why use Sepolia instead of Mainnet?**
A: During development/testing, Sepolia avoids gas costs and allows easy testing. Production uses mainnet.

**Q: What if on-chain balance is higher than database?**
A: This is actually good! It means the platform is over-reserved. Status will still show VERIFIED.

**Q: What if database shows more than blockchain?**
A: This indicates a serious issue - users have been credited more than the platform holds. Status: MISMATCH.

**Q: How often does verification run?**
A: Every time the `/report` or `/onchain` endpoint is called. No background jobs needed.

**Q: Can users verify their own balance is included?**
A: Yes! Users can check that their balance hash exists in the Merkle tree using the Merkle proof.

**Q: What about privacy?**
A: Reserve wallets are public, but individual user balances are anonymized in the Merkle tree.

## Conclusion

On-chain reserve tracking provides the highest level of transparency possible - allowing anyone to verify that the DPG platform truly holds the reserves it claims. Combined with Merkle tree verification, this creates a fully auditable, trustless proof of reserves system.

**Trust, but verify. Better yet, just verify!** 🔍⛓️
