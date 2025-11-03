"""
Wallet Service
Handles wallet creation, encryption, and blockchain interactions
"""
from eth_account import Account
from web3 import Web3
from cryptography.fernet import Fernet
import secrets
import os
from typing import Tuple, Dict
from dotenv import load_dotenv

load_dotenv()

# Encryption key for private keys (MUST be stored securely in production)
ENCRYPTION_KEY = os.getenv("WALLET_ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generate a key if not exists (for development)
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"\n{'='*70}")
    print(f"⚠️  WARNING: No WALLET_ENCRYPTION_KEY in .env file!")
    print(f"⚠️  Using temporary key: {ENCRYPTION_KEY[:20]}...")
    print(f"⚠️  Add this to backend/.env to persist wallets:")
    print(f"WALLET_ENCRYPTION_KEY={ENCRYPTION_KEY}")
    print(f"{'='*70}\n")

try:
    cipher_suite = Fernet(ENCRYPTION_KEY.encode())
except Exception as e:
    print(f"❌ Failed to initialize encryption: {e}")
    print(f"⚠️  Key length: {len(ENCRYPTION_KEY)} chars")
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


def encrypt_private_key(private_key: str) -> str:
    """
    Encrypt a private key for storage
    
    Args:
        private_key: Plain text private key
        
    Returns:
        str: Encrypted private key (base64)
    """
    encrypted = cipher_suite.encrypt(private_key.encode())
    return encrypted.decode()


def decrypt_private_key(encrypted_key: str) -> str:
    """
    Decrypt a private key
    
    Args:
        encrypted_key: Encrypted private key (base64)
        
    Returns:
        str: Decrypted private key
    """
    try:
        decrypted = cipher_suite.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except Exception as e:
        error_msg = str(e)
        if 'Invalid' in error_msg or 'token' in error_msg:
            raise ValueError(
                "Cannot decrypt wallet - encryption key has changed. "
                "This wallet was encrypted with a different key. "
                "To fix: 1) Copy the WALLET_ENCRYPTION_KEY from backend console startup, "
                "2) Add it to backend/.env, 3) Restart backend. "
                "Or re-import your wallet with the current key."
            )
        else:
            raise ValueError(f"Decryption failed: {error_msg}")


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
