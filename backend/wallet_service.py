"""
Wallet Service
Handles wallet creation, encryption, and blockchain interactions
"""
from eth_account import Account
from web3 import Web3
import secrets
import os
from typing import Tuple, Dict
from dotenv import load_dotenv

# Import enterprise-grade encryption
from crypto_manager import encrypt_private_key, decrypt_private_key, get_crypto_manager

load_dotenv()

# Validate encryption on startup
try:
    crypto_manager = get_crypto_manager()
    print("✅ Enterprise encryption initialized successfully")
except Exception as e:
    print(f"❌ CRITICAL: Encryption initialization failed!")
    print(f"   Error: {e}")
    print()
    print("   Run: python backend/generate_master_key.py")
    raise


def generate_ethereum_wallet() -> Tuple[str, str]:
    """
    Generate a new Ethereum wallet (address + private key)
    
    Returns:
        Tuple[str, str]: (public_address, private_key)
    """
    # Enable unaudited features for account creation
    Account.enable_unaudited_hdwallet_features()
    
    # Generate random private key
    private_key = "0x" + secrets.token_hex(32)
    
    # Create account from private key
    account = Account.from_key(private_key)
    
    return account.address, private_key


def get_wallet_balance(address: str, network: str = "mainnet") -> Dict:
    """
    Get wallet balance from blockchain
    
    Args:
        address: Ethereum address
        network: Network to check (mainnet, goerli, sepolia, polygon)
        
    Returns:
        Dict with balance information
    """
    # RPC endpoints (you can use Infura, Alchemy, or public RPCs)
    rpc_urls = {
        "mainnet": "https://eth.llamarpc.com",  # Public RPC
        "sepolia": "https://rpc.sepolia.org",
        "polygon": "https://polygon-rpc.com",
    }
    
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_urls.get(network, rpc_urls["mainnet"])))
        
        if not w3.is_connected():
            return {"error": "Failed to connect to network", "balance": "0"}
        
        # Get balance in Wei
        balance_wei = w3.eth.get_balance(address)
        
        # Convert to ETH
        balance_eth = w3.from_wei(balance_wei, 'ether')
        
        return {
            "address": address,
            "balance_wei": str(balance_wei),
            "balance_eth": str(balance_eth),
            "network": network
        }
    except Exception as e:
        return {"error": str(e), "balance": "0"}


def validate_ethereum_address(address: str) -> bool:
    """
    Validate if a string is a valid Ethereum address
    
    Args:
        address: Address to validate
        
    Returns:
        bool: True if valid
    """
    try:
        return Web3.is_address(address)
    except:
        return False


# For Bitcoin/other chains support (future expansion)
def generate_bitcoin_wallet():
    """
    Generate Bitcoin wallet (placeholder for future implementation)
    """
    # Will implement with bitcoin libraries
    pass
