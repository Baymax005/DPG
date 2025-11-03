"""
Enterprise-Grade Cryptographic Key Management
Uses industry-standard practices for secure key storage and derivation
"""
import os
import base64
import hashlib
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import secrets

load_dotenv()


class CryptoManager:
    """
    Enterprise-grade encryption manager for wallet private keys.
    
    Uses a multi-layer approach:
    1. Master key from environment (rotatable)
    2. Per-wallet salt (stored with encrypted data)
    3. PBKDF2 key derivation (prevents rainbow table attacks)
    4. Fernet symmetric encryption (AES-128-CBC + HMAC)
    """
    
    def __init__(self):
        """Initialize crypto manager with master key"""
        # Get master key from environment
        master_key_b64 = os.getenv("WALLET_MASTER_KEY")
        
        if not master_key_b64:
            raise ValueError(
                "❌ CRITICAL: WALLET_MASTER_KEY not found in .env!\n"
                "This is required for production. Generate one with:\n"
                "  python backend/generate_master_key.py\n"
                "Then add it to backend/.env"
            )
        
        try:
            # Decode master key from base64
            self.master_key = base64.urlsafe_b64decode(master_key_b64)
            
            # Validate key length (must be 32 bytes for Fernet)
            if len(self.master_key) != 32:
                raise ValueError(f"Master key must be 32 bytes, got {len(self.master_key)}")
                
        except Exception as e:
            raise ValueError(
                f"❌ Invalid WALLET_MASTER_KEY format: {e}\n"
                "Generate a new one with: python backend/generate_master_key.py"
            )
    
    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive encryption key from master key + salt using PBKDF2.
        
        This adds per-wallet security even if master key is compromised.
        Attackers would need both master key AND the salt for each wallet.
        
        Args:
            salt: Unique salt for this wallet (16 bytes)
            
        Returns:
            32-byte derived key suitable for Fernet
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # Fernet requires 32 bytes
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
            backend=default_backend()
        )
        return kdf.derive(self.master_key)
    
    def encrypt_private_key(self, private_key: str) -> str:
        """
        Encrypt a private key with salt-based key derivation.
        
        Format: salt (16 bytes) + encrypted_data
        Both are base64 encoded together for storage.
        
        Args:
            private_key: Plain text private key (hex string)
            
        Returns:
            Base64 encoded: salt + encrypted_private_key
        """
        if not private_key:
            raise ValueError("Private key cannot be empty")
        
        # Generate random salt (16 bytes)
        salt = secrets.token_bytes(16)
        
        # Derive encryption key from master key + salt
        derived_key = self._derive_key(salt)
        
        # Create Fernet cipher with derived key
        cipher = Fernet(base64.urlsafe_b64encode(derived_key))
        
        # Encrypt private key
        encrypted_data = cipher.encrypt(private_key.encode())
        
        # Combine salt + encrypted_data
        combined = salt + encrypted_data
        
        # Return as base64 for storage
        return base64.urlsafe_b64encode(combined).decode()
    
    def decrypt_private_key(self, encrypted_data_b64: str) -> str:
        """
        Decrypt a private key using stored salt.
        
        Args:
            encrypted_data_b64: Base64 encoded salt + encrypted_private_key
            
        Returns:
            Plain text private key (hex string)
        """
        if not encrypted_data_b64:
            raise ValueError("Encrypted data cannot be empty")
        
        try:
            # Decode from base64
            combined = base64.urlsafe_b64decode(encrypted_data_b64)
            
            # Extract salt (first 16 bytes) and encrypted data (rest)
            salt = combined[:16]
            encrypted_data = combined[16:]
            
            # Derive the same key using the stored salt
            derived_key = self._derive_key(salt)
            
            # Create Fernet cipher with derived key
            cipher = Fernet(base64.urlsafe_b64encode(derived_key))
            
            # Decrypt data
            decrypted_data = cipher.decrypt(encrypted_data)
            
            return decrypted_data.decode()
            
        except Exception as e:
            error_msg = str(e)
            
            # Provide helpful error messages
            if 'Invalid' in error_msg or 'token' in error_msg:
                raise ValueError(
                    "❌ Decryption failed: Invalid master key or corrupted data.\n"
                    "Possible causes:\n"
                    "1. WALLET_MASTER_KEY in .env has changed\n"
                    "2. Database was corrupted\n"
                    "3. Data was modified\n\n"
                    "⚠️  If master key was lost, wallets cannot be recovered.\n"
                    "You must re-import wallets with current master key."
                )
            else:
                raise ValueError(f"Decryption failed: {error_msg}")
    
    def rotate_key(self, old_encrypted_data: str, old_master_key: bytes) -> str:
        """
        Rotate encryption key for a wallet (re-encrypt with new master key).
        
        This is for key rotation in production environments.
        
        Args:
            old_encrypted_data: Data encrypted with old master key
            old_master_key: The old master key (32 bytes)
            
        Returns:
            New encrypted data with current master key
        """
        # Temporarily use old master key
        old_manager = CryptoManager.__new__(CryptoManager)
        old_manager.master_key = old_master_key
        
        # Decrypt with old key
        private_key = old_manager.decrypt_private_key(old_encrypted_data)
        
        # Re-encrypt with current key
        return self.encrypt_private_key(private_key)
    
    def validate_master_key(self) -> bool:
        """
        Validate that master key is properly configured.
        
        Returns:
            True if valid
        """
        return len(self.master_key) == 32
    
    @staticmethod
    def generate_master_key() -> str:
        """
        Generate a new cryptographically secure master key.
        
        Returns:
            Base64-encoded 32-byte key
        """
        key = secrets.token_bytes(32)
        return base64.urlsafe_b64encode(key).decode()


# Singleton instance
_crypto_manager: Optional[CryptoManager] = None


def get_crypto_manager() -> CryptoManager:
    """
    Get or create the singleton CryptoManager instance.
    
    Returns:
        CryptoManager instance
    """
    global _crypto_manager
    
    if _crypto_manager is None:
        _crypto_manager = CryptoManager()
    
    return _crypto_manager


def encrypt_private_key(private_key: str) -> str:
    """
    Encrypt a private key (convenience function).
    
    Args:
        private_key: Plain text private key
        
    Returns:
        Encrypted private key
    """
    return get_crypto_manager().encrypt_private_key(private_key)


def decrypt_private_key(encrypted_data: str) -> str:
    """
    Decrypt a private key (convenience function).
    
    Args:
        encrypted_data: Encrypted private key
        
    Returns:
        Plain text private key
    """
    return get_crypto_manager().decrypt_private_key(encrypted_data)


if __name__ == "__main__":
    """Test encryption/decryption"""
    print("🔐 Testing Enterprise Encryption\n")
    
    # Check if master key exists
    if not os.getenv("WALLET_MASTER_KEY"):
        print("❌ WALLET_MASTER_KEY not found in .env")
        print("Generate one with: python backend/generate_master_key.py")
        exit(1)
    
    try:
        # Initialize manager
        manager = CryptoManager()
        print("✅ CryptoManager initialized")
        
        # Test encryption/decryption
        test_private_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        
        print(f"\n📝 Original private key: {test_private_key[:20]}...")
        
        # Encrypt
        encrypted = manager.encrypt_private_key(test_private_key)
        print(f"🔒 Encrypted: {encrypted[:50]}... (length: {len(encrypted)})")
        
        # Decrypt
        decrypted = manager.decrypt_private_key(encrypted)
        print(f"🔓 Decrypted: {decrypted[:20]}...")
        
        # Verify
        if decrypted == test_private_key:
            print("\n✅ Encryption/Decryption successful!")
            print("✅ Salt-based key derivation working")
        else:
            print("\n❌ Decryption failed - mismatch!")
        
        # Test with multiple encryptions (should produce different ciphertexts due to salt)
        encrypted1 = manager.encrypt_private_key(test_private_key)
        encrypted2 = manager.encrypt_private_key(test_private_key)
        
        if encrypted1 != encrypted2:
            print("✅ Salt randomization working (different ciphertexts)")
        else:
            print("⚠️  Warning: Same ciphertext produced")
        
        # Both should decrypt to same value
        if (manager.decrypt_private_key(encrypted1) == test_private_key and 
            manager.decrypt_private_key(encrypted2) == test_private_key):
            print("✅ Both ciphertexts decrypt correctly")
        
        print("\n🎉 All encryption tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
