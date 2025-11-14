"""
Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

# ============================================
# User Schemas
# ============================================

class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """
        Password must contain:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)"""
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_verified: bool
    kyc_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token payload"""
    user_id: Optional[str] = None
    email: Optional[str] = None

# ============================================
# Wallet Schemas
# ============================================

class WalletCreate(BaseModel):
    """Schema for creating a wallet"""
    currency_code: str = Field(..., max_length=10)
    wallet_type: str = Field(..., pattern="^(fiat|crypto)$")

class WalletResponse(BaseModel):
    """Schema for wallet response"""
    id: str
    currency_code: str
    wallet_type: str
    balance: str  # String to preserve precision
    address: Optional[str]
    created_at: datetime
    
    @field_validator('balance', mode='before')
    @classmethod
    def convert_decimal_to_string(cls, v):
        """Convert Decimal to string"""
        if v is None:
            return "0"
        return str(v)
    
    class Config:
        from_attributes = True

# ============================================
# Generic Responses
# ============================================

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    details: Optional[dict] = None

# ============================================
# Transaction Schemas
# ============================================

class DepositRequest(BaseModel):
    """Schema for deposit request"""
    wallet_id: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    reference_id: Optional[str] = None

class WithdrawalRequest(BaseModel):
    """Schema for withdrawal request"""
    wallet_id: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    destination_address: Optional[str] = None  # For crypto withdrawals

class TransferRequest(BaseModel):
    """Schema for transfer between wallets"""
    from_wallet_id: str
    to_wallet_id: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = None

class SendRequest(BaseModel):
    """Schema for sending to external blockchain address"""
    wallet_id: str
    to_address: str = Field(..., min_length=26, max_length=64)
    amount: float = Field(..., gt=0)
    network: str = Field(..., pattern="^(sepolia|amoy|ethereum|polygon)$")
    description: Optional[str] = None
    
    @field_validator('to_address')
    @classmethod
    def validate_address(cls, v):
        """Basic address format validation"""
        v = v.strip()
        # Ethereum address (0x + 40 hex chars)
        if v.startswith('0x'):
            if len(v) != 42:
                raise ValueError('Ethereum address must be 42 characters (0x + 40 hex)')
            if not all(c in '0123456789abcdefABCDEF' for c in v[2:]):
                raise ValueError('Invalid Ethereum address format')
        # Bitcoin address validation (basic)
        elif v.startswith(('1', '3', 'bc1')):
            if not (26 <= len(v) <= 62):
                raise ValueError('Invalid Bitcoin address length')
        else:
            raise ValueError('Address must start with 0x (Ethereum) or 1/3/bc1 (Bitcoin)')
        return v

class TransactionResponse(BaseModel):
    """Schema for transaction response"""
    id: str
    wallet_id: str
    type: str
    amount: str
    fee: str
    status: str
    description: Optional[str]
    tx_hash: Optional[str]
    reference_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    @field_validator('amount', 'fee', mode='before')
    @classmethod
    def convert_decimal_to_string(cls, v):
        """Convert Decimal to string"""
        if v is None:
            return "0"
        return str(v)
    
    class Config:
        from_attributes = True
