"""
Reserve Wallet Configuration
Configure reserve wallet addresses for Proof of Reserves tracking

IMPORTANT: Update these addresses to match your actual reserve wallets!
"""
import os
from typing import Dict, List

# ==============================================================================
# RESERVE WALLET ADDRESSES
# ==============================================================================
# These are the wallet addresses that hold platform reserves
# The on-chain verification will check these addresses on the blockchain
# ==============================================================================

# Option 1: Hardcoded addresses (easy to see and change)
RESERVE_WALLETS: Dict[str, List[str]] = {
    # Ethereum (ETH)
    'ETH': [
        '0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765',  # ✅ Your DPG wallet (umerdon67@gmail.com)
        # Add more ETH reserve wallets if you have multiple:
        # '0xYourMetaMaskWallet',
        # '0xYourColdWallet',
    ],
    
    # Tether USD (USDT - ERC-20)
    'USDT': [
        '0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765',  # ✅ Same wallet for USDT
    ],
    
    # USD Coin (USDC - ERC-20)
    'USDC': [
        '0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765',  # ✅ Same wallet for USDC
    ],
    
    # Polygon MATIC (if/when you add Polygon support)
    'MATIC': [
        '0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765',  # ✅ Same wallet for MATIC
    ],
}

# Option 2: Environment variables (for production security)
# These will override the hardcoded addresses above if set in .env
RESERVE_WALLETS_FROM_ENV = {
    'ETH': os.getenv('ETH_RESERVE_WALLETS', '').split(',') if os.getenv('ETH_RESERVE_WALLETS') else None,
    'USDT': os.getenv('USDT_RESERVE_WALLETS', '').split(',') if os.getenv('USDT_RESERVE_WALLETS') else None,
    'USDC': os.getenv('USDC_RESERVE_WALLETS', '').split(',') if os.getenv('USDC_RESERVE_WALLETS') else None,
    'MATIC': os.getenv('MATIC_RESERVE_WALLETS', '').split(',') if os.getenv('MATIC_RESERVE_WALLETS') else None,
}

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_reserve_wallets(currency: str = None) -> Dict[str, List[str]]:
    """
    Get reserve wallet addresses with environment variable override
    
    Args:
        currency: Optional currency code to get wallets for specific currency
        
    Returns:
        Dictionary of currency -> list of wallet addresses
    """
    # Merge hardcoded and environment wallets (env takes precedence)
    final_wallets = {}
    
    for curr in RESERVE_WALLETS.keys():
        # Start with hardcoded
        wallets = RESERVE_WALLETS[curr].copy()
        
        # Override with env if exists
        if RESERVE_WALLETS_FROM_ENV.get(curr):
            env_wallets = [w.strip() for w in RESERVE_WALLETS_FROM_ENV[curr] if w.strip()]
            if env_wallets:
                wallets = env_wallets
        
        final_wallets[curr] = wallets
    
    # Return specific currency or all
    if currency:
        return {currency: final_wallets.get(currency, [])}
    return final_wallets


def validate_address(address: str) -> bool:
    """
    Validate Ethereum address format
    
    Args:
        address: Ethereum address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not address or not isinstance(address, str):
        return False
    
    # Must start with 0x and be 42 characters (0x + 40 hex chars)
    if not address.startswith('0x') or len(address) != 42:
        return False
    
    # Must be valid hex
    try:
        int(address, 16)
        return True
    except ValueError:
        return False


def print_reserve_config():
    """Print current reserve wallet configuration for debugging"""
    print("\n" + "="*70)
    print("🏦 RESERVE WALLET CONFIGURATION")
    print("="*70)
    
    wallets = get_reserve_wallets()
    
    for currency, addresses in wallets.items():
        print(f"\n{currency}:")
        if not addresses or addresses == ['0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb8']:
            print(f"  ⚠️  WARNING: Using placeholder address!")
            print(f"  ⚠️  Update in backend/reserve_config.py")
        
        for i, addr in enumerate(addresses, 1):
            valid = "✅" if validate_address(addr) else "❌"
            print(f"  {i}. {valid} {addr}")
            
            # Check if it's the placeholder
            if addr == '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb8':
                print(f"     ⚠️  This is a PLACEHOLDER - update it!")
    
    print("\n" + "="*70)
    print("💡 TIP: You can also set reserve wallets in .env file:")
    print("   ETH_RESERVE_WALLETS=0xAddress1,0xAddress2")
    print("   USDT_RESERVE_WALLETS=0xAddress1")
    print("="*70 + "\n")


# ==============================================================================
# QUICK SETUP GUIDE
# ==============================================================================
"""
HOW TO UPDATE RESERVE WALLET ADDRESSES:

1. FIND YOUR WALLET ADDRESS:
   - If using MetaMask: Copy your wallet address from MetaMask
   - If using DPG wallet: Check your database or wallet list in the app
   - If using hardware wallet: Get address from device

2. UPDATE THIS FILE:
   - Replace '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb8' with your actual address
   - You can add multiple addresses per currency (for cold storage, etc.)

3. OR USE ENVIRONMENT VARIABLES (recommended for production):
   Add to your .env file:
   ```
   ETH_RESERVE_WALLETS=0xYourActualAddress1,0xYourActualAddress2
   USDT_RESERVE_WALLETS=0xYourActualAddress
   USDC_RESERVE_WALLETS=0xYourActualAddress
   ```

4. VERIFY:
   Run: python -c "from reserve_config import print_reserve_config; print_reserve_config()"

EXAMPLES:

# Single wallet for all currencies (common for testing):
RESERVE_WALLETS = {
    'ETH': ['0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765'],
    'USDT': ['0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765'],
    'USDC': ['0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765'],
}

# Multiple wallets (hot + cold storage):
RESERVE_WALLETS = {
    'ETH': [
        '0xYourHotWallet',   # Hot wallet for daily operations
        '0xYourColdWallet', # Cold storage
    ],
    'USDT': ['0xYourHotWallet'],
    'USDC': ['0xYourHotWallet'],
}

# Using your MetaMask wallet:
RESERVE_WALLETS = {
    'ETH': ['0xYourMetaMaskAddress'],
    'USDT': ['0xYourMetaMaskAddress'],
    'USDC': ['0xYourMetaMaskAddress'],
}
"""

# ==============================================================================
# RUN THIS FILE TO CHECK YOUR CONFIGURATION
# ==============================================================================
if __name__ == "__main__":
    print_reserve_config()
