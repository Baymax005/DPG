"""
Database Models
Defines all database tables
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid
import enum

def generate_uuid():
    """Generate UUID for primary keys"""
    return str(uuid.uuid4())

class KYCStatus(str, enum.Enum):
    """KYC verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    
    # Personal info
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    kyc_status = Column(SQLEnum(KYCStatus), default=KYCStatus.PENDING)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    wallets = relationship("Wallet", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"

class WalletType(str, enum.Enum):
    """Wallet type"""
    FIAT = "fiat"
    CRYPTO = "crypto"

class Wallet(Base):
    """Wallet model - stores both fiat and crypto wallets"""
    __tablename__ = "wallets"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Wallet details
    currency_code = Column(String, nullable=False)  # USD, BTC, ETH, etc.
    wallet_type = Column(SQLEnum(WalletType), nullable=False)
    balance = Column(Numeric(28, 18), default=0)  # High precision for crypto
    
    # For crypto wallets
    address = Column(String, nullable=True, unique=True)  # Public address
    private_key_encrypted = Column(String, nullable=True)  # Encrypted private key
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="wallets")
    
    def __repr__(self):
        return f"<Wallet {self.currency_code} - {self.wallet_type}>"

class TransactionType(str, enum.Enum):
    """Transaction types"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    CONVERSION = "conversion"
    FEE = "fee"

class TransactionStatus(str, enum.Enum):
    """Transaction status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Transaction(Base):
    """Transaction model"""
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    wallet_id = Column(String, ForeignKey("wallets.id"), nullable=False)
    
    # Transaction details
    type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Numeric(28, 18), nullable=False)
    fee = Column(Numeric(28, 18), default=0)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    
    # External references
    tx_hash = Column(String, nullable=True)  # Blockchain transaction hash
    reference_id = Column(String, nullable=True)  # External reference
    network = Column(String, nullable=True, default="sepolia")  # Blockchain network
    
    # Metadata
    description = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Transaction {self.type} - {self.amount}>"
