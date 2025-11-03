# 🦊 MetaMask Integration Guide for DPG

## Architecture Overview

DPG uses a **HYBRID** approach (as per HYBRID_ARCHITECTURE.md):

### ✅ **Custodial Wallets** (Current - Phase 1)
- Backend manages private keys (encrypted)
- **Instant trading** - 0 gas fees, <10ms execution
- Balances in PostgreSQL database
- Daily proof of reserves on blockchain

### ✅ **Self-Custody Option** (Phase 2 - Add MetaMask)
- Users can **deposit** from MetaMask
- Users can **withdraw** to MetaMask
- Users **choose**: Speed (custodial) vs Control (self-custody)

---

## Why Both Approaches?

### Custodial (Current)
**Use Case:** Daily trading, frequent transactions
- ✅ Instant execution (no waiting for blocks)
- ✅ FREE trades (no gas fees)
- ✅ Better UX for non-crypto users
- ⚠️ Platform holds keys (but audited daily)

### MetaMask Integration (Add)
**Use Case:** Large amounts, long-term holding, full control
- ✅ User controls keys (true self-custody)
- ✅ Can withdraw anytime
- ✅ Works with hardware wallets
- ⚠️ Pay gas fees for deposits/withdrawals
- ⚠️ Slower (blockchain confirmation time)

---

## Implementation Plan

### Phase 1: MetaMask Detection & Connection

**Frontend (React + Web3.js):**

```typescript
// src/utils/metamask.ts
import Web3 from 'web3';

export class MetaMaskService {
  private web3: Web3 | null = null;
  
  // Check if MetaMask is installed
  isInstalled(): boolean {
    return typeof window.ethereum !== 'undefined';
  }
  
  // Connect to MetaMask
  async connect(): Promise<string> {
    if (!this.isInstalled()) {
      throw new Error('MetaMask is not installed!');
    }
    
    // Request account access
    const accounts = await window.ethereum.request({
      method: 'eth_requestAccounts'
    });
    
    this.web3 = new Web3(window.ethereum);
    return accounts[0]; // User's address
  }
  
  // Get current account
  async getAccount(): Promise<string | null> {
    if (!this.web3) return null;
    
    const accounts = await this.web3.eth.getAccounts();
    return accounts[0] || null;
  }
  
  // Get balance
  async getBalance(address: string): Promise<string> {
    if (!this.web3) throw new Error('Not connected');
    
    const balance = await this.web3.eth.getBalance(address);
    return this.web3.utils.fromWei(balance, 'ether');
  }
  
  // Sign message (for verification)
  async signMessage(address: string, message: string): Promise<string> {
    if (!this.web3) throw new Error('Not connected');
    
    return await this.web3.eth.personal.sign(message, address, '');
  }
  
  // Send transaction (deposit to DPG)
  async sendTransaction(to: string, amount: string): Promise<string> {
    if (!this.web3) throw new Error('Not connected');
    
    const from = await this.getAccount();
    if (!from) throw new Error('No account selected');
    
    const amountWei = this.web3.utils.toWei(amount, 'ether');
    
    const txHash = await this.web3.eth.sendTransaction({
      from,
      to,
      value: amountWei
    });
    
    return txHash.transactionHash;
  }
}
```

**Usage in Component:**

```typescript
// src/components/WalletConnect.tsx
import React, { useState } from 'react';
import { MetaMaskService } from '../utils/metamask';

export const WalletConnect: React.FC = () => {
  const [address, setAddress] = useState<string | null>(null);
  const [balance, setBalance] = useState<string>('0');
  const metamask = new MetaMaskService();
  
  const handleConnect = async () => {
    try {
      if (!metamask.isInstalled()) {
        alert('Please install MetaMask: https://metamask.io');
        return;
      }
      
      const addr = await metamask.connect();
      setAddress(addr);
      
      const bal = await metamask.getBalance(addr);
      setBalance(bal);
      
      // Verify ownership by signing message
      const message = `Verify ownership of ${addr} for DPG`;
      const signature = await metamask.signMessage(addr, message);
      
      // Send to backend for verification
      await fetch('/api/v1/wallets/verify-metamask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address: addr, signature, message })
      });
      
    } catch (error) {
      console.error('MetaMask connection failed:', error);
    }
  };
  
  return (
    <div>
      {!address ? (
        <button onClick={handleConnect}>
          🦊 Connect MetaMask
        </button>
      ) : (
        <div>
          <p>Connected: {address.slice(0, 6)}...{address.slice(-4)}</p>
          <p>Balance: {parseFloat(balance).toFixed(4)} ETH</p>
        </div>
      )}
    </div>
  );
};
```

---

### Phase 2: Deposit from MetaMask

**Frontend:**

```typescript
// src/components/DepositFromMetaMask.tsx
export const DepositFromMetaMask: React.FC = () => {
  const [amount, setAmount] = useState('');
  const metamask = new MetaMaskService();
  
  // Get DPG deposit address from backend
  const getDPGDepositAddress = async () => {
    const response = await fetch('/api/v1/wallets/deposit-address', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    return data.deposit_address; // DPG's smart contract address
  };
  
  const handleDeposit = async () => {
    try {
      // Get DPG deposit address
      const dpgAddress = await getDPGDepositAddress();
      
      // Send ETH from MetaMask to DPG
      const txHash = await metamask.sendTransaction(dpgAddress, amount);
      
      // Notify backend about deposit
      await fetch('/api/v1/transactions/deposit-notify', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tx_hash: txHash,
          amount: amount,
          network: 'sepolia' // or 'ethereum'
        })
      });
      
      alert('Deposit initiated! Waiting for confirmation...');
      
    } catch (error) {
      console.error('Deposit failed:', error);
    }
  };
  
  return (
    <div>
      <input 
        type="number" 
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        placeholder="Amount (ETH)"
      />
      <button onClick={handleDeposit}>
        📥 Deposit from MetaMask
      </button>
    </div>
  );
};
```

**Backend API:**

```python
# backend/wallet_routes.py

@router.post("/deposit-address")
async def get_deposit_address(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get DPG deposit address for MetaMask deposits
    
    Returns the smart contract address where users can send funds
    """
    # Get user's DPG wallet
    wallet = db.query(Wallet).filter(
        Wallet.user_id == current_user.id,
        Wallet.currency_code == "ETH"
    ).first()
    
    if not wallet:
        raise HTTPException(404, "ETH wallet not found")
    
    # Return DPG's deposit contract address
    # This is a unique address per user or a pooled address with memo
    return {
        "deposit_address": wallet.address,  # User's assigned deposit address
        "network": "sepolia",  # or "ethereum" for mainnet
        "min_deposit": "0.001",  # Minimum deposit amount
        "note": "Send only ETH to this address. Deposits are credited after 12 confirmations."
    }


@router.post("/deposit-notify")
async def notify_deposit(
    deposit_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    User notifies backend about a MetaMask deposit
    
    Backend will:
    1. Monitor this tx_hash for confirmations
    2. Credit user's balance once confirmed
    """
    tx_hash = deposit_data.get('tx_hash')
    amount = deposit_data.get('amount')
    network = deposit_data.get('network', 'sepolia')
    
    # Create pending deposit record
    transaction = Transaction(
        wallet_id=deposit_data['wallet_id'],
        type=TransactionType.DEPOSIT,
        amount=Decimal(amount),
        status=TransactionStatus.PENDING,
        tx_hash=tx_hash,
        network=network,
        description="MetaMask deposit"
    )
    
    db.add(transaction)
    db.commit()
    
    # Background task will monitor and credit once confirmed
    return {
        "message": "Deposit noted! We'll credit your account once confirmed.",
        "tx_hash": tx_hash,
        "explorer_url": f"https://sepolia.etherscan.io/tx/{tx_hash}",
        "estimated_time": "2-5 minutes"
    }
```

---

### Phase 3: Withdraw to MetaMask

**Frontend:**

```typescript
// src/components/WithdrawToMetaMask.tsx
export const WithdrawToMetaMask: React.FC = () => {
  const [amount, setAmount] = useState('');
  const [address, setAddress] = useState('');
  const metamask = new MetaMaskService();
  
  // Auto-fill with MetaMask address
  const useMyMetaMaskAddress = async () => {
    const addr = await metamask.getAccount();
    if (addr) setAddress(addr);
  };
  
  const handleWithdraw = async () => {
    try {
      const response = await fetch('/api/v1/transactions/withdraw-to-address', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          to_address: address,
          amount: amount,
          network: 'sepolia'
        })
      });
      
      const data = await response.json();
      
      alert(`Withdrawal initiated!\nTX: ${data.tx_hash}`);
      
    } catch (error) {
      console.error('Withdrawal failed:', error);
    }
  };
  
  return (
    <div>
      <input 
        type="text" 
        value={address}
        onChange={(e) => setAddress(e.target.value)}
        placeholder="0x... (Ethereum address)"
      />
      <button onClick={useMyMetaMaskAddress}>
        Use My MetaMask Address
      </button>
      
      <input 
        type="number" 
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        placeholder="Amount (ETH)"
      />
      
      <button onClick={handleWithdraw}>
        📤 Withdraw to Address
      </button>
    </div>
  );
};
```

---

## Amount Display Fix

### Frontend Number Formatting

```typescript
// src/utils/format.ts
export const formatCrypto = (value: string | number, decimals: number = 8): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  
  // For very small numbers, use more decimals
  if (num < 0.01 && num > 0) {
    return num.toFixed(decimals);
  }
  
  // For normal numbers
  return num.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: decimals
  });
};

// Usage:
// formatCrypto("0.001") => "0.00100000"
// formatCrypto("0.001", 4) => "0.0010"
// formatCrypto("1.5") => "1.50"
// formatCrypto("1234.56789") => "1,234.56789"
```

### Display in Table

```typescript
// In Transaction History component
<td>{formatCrypto(transaction.amount, 8)}</td>
<td>{formatCrypto(transaction.fee, 8)}</td>
```

---

## Backend API Enhancement

Already done! The backend returns full precision:

```python
# schemas.py - TransactionResponse
@field_validator('amount', 'fee', mode='before')
@classmethod
def convert_decimal_to_string(cls, v):
    """Convert Decimal to string - preserves full precision"""
    if v is None:
        return "0"
    return str(v)  # Returns "0.001000000000000000"
```

---

## User Flow

### Option 1: Custodial (Current - Fast)
```
1. User registers → Backend creates wallet
2. User deposits → Instant credit (internal)
3. User trades → Instant, FREE
4. User withdraws → To bank or blockchain
```

### Option 2: MetaMask (Add - Full Control)
```
1. User connects MetaMask
2. User deposits from MetaMask → DPG address
3. Confirmations (12 blocks) → Credit balance
4. User can trade (same as custodial)
5. User withdraws → Back to MetaMask
```

---

## Deployment Checklist

### Backend
- [ ] Add `/deposit-address` endpoint
- [ ] Add `/deposit-notify` endpoint
- [ ] Add `/withdraw-to-address` endpoint (already exists as `/send`)
- [ ] Add `/verify-metamask` endpoint
- [ ] Deploy deposit monitoring service
- [ ] Test on Sepolia testnet

### Frontend
- [ ] Install `web3` package: `npm install web3`
- [ ] Add MetaMask detection
- [ ] Add "Connect MetaMask" button
- [ ] Add "Deposit from MetaMask" UI
- [ ] Add "Withdraw to MetaMask" UI
- [ ] Fix amount formatting (`formatCrypto` function)
- [ ] Update transaction table to show full precision
- [ ] Add network selection (Sepolia/Ethereum)

### Smart Contracts (Phase 2)
- [ ] Deploy deposit contract on Sepolia
- [ ] Deploy deposit contract on Ethereum mainnet
- [ ] Implement multi-sig withdrawal contract
- [ ] Audit contracts (CertiK/OpenZeppelin)

---

## Priority

**Immediate (This Week):**
1. ✅ Fix amount display - Add `formatCrypto()` function to frontend
2. ✅ Add "Connect MetaMask" button - Basic detection

**Short Term (Next 2 Weeks):**
3. ✅ Deposit from MetaMask - Full flow
4. ✅ Withdraw to MetaMask - Use existing `/send` endpoint

**Medium Term (Q1 2026):**
5. Smart contract deployment
6. Automated deposit monitoring
7. Multi-sig security

---

## Summary

✅ **Keep custodial wallets** - For fast, free trading  
✅ **Add MetaMask integration** - For deposits/withdrawals and self-custody  
✅ **Fix amount display** - Show full precision (0.001 instead of 0.00)  
✅ **Hybrid approach** - Users choose: Speed vs Control  

**This matches the HYBRID_ARCHITECTURE.md perfectly!** 🎉
