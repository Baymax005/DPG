"""
Wallet Routes
Handles wallet creation and management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Wallet, WalletType
from schemas import WalletCreate, WalletResponse
from auth_routes import get_current_user
from wallet_service import (
    generate_ethereum_wallet,
    encrypt_private_key,
    get_wallet_balance,
    validate_ethereum_address
)

router = APIRouter(prefix="/api/v1/wallets", tags=["Wallets"])


@router.post("/create", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(
    wallet_data: WalletCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new wallet for the current user
    
    - **currency_code**: Currency code (ETH, BTC, MATIC, USDT, USD, etc.)
    - **wallet_type**: Type of wallet (fiat or crypto)
    """
    # Check if user already has this wallet
    existing_wallet = db.query(Wallet).filter(
        Wallet.user_id == current_user.id,
        Wallet.currency_code == wallet_data.currency_code.upper()
    ).first()
    
    if existing_wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Wallet for {wallet_data.currency_code} already exists"
        )
    
    # Create wallet based on type
    new_wallet = Wallet(
        user_id=current_user.id,
        currency_code=wallet_data.currency_code.upper(),
        wallet_type=WalletType(wallet_data.wallet_type),
        balance=0
    )
    
    # Generate blockchain address for crypto wallets
    if wallet_data.wallet_type == "crypto":
        # Support for different crypto currencies
        if wallet_data.currency_code.upper() in ["ETH", "MATIC", "USDT", "USDC"]:
            # Ethereum-compatible chains (same address format)
            public_address, private_key = generate_ethereum_wallet()
            
            # Encrypt and store private key
            encrypted_key = encrypt_private_key(private_key)
            
            new_wallet.address = public_address
            new_wallet.private_key_encrypted = encrypted_key
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Currency {wallet_data.currency_code} not supported yet"
            )
    
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    
    return new_wallet


@router.get("/", response_model=List[WalletResponse])
async def get_user_wallets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all wallets for the current user
    """
    wallets = db.query(Wallet).filter(Wallet.user_id == current_user.id).all()
    return wallets


@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
    wallet_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific wallet by ID
    """
    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    return wallet


@router.get("/{wallet_id}/balance")
async def get_wallet_balance_live(
    wallet_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get live balance from blockchain for crypto wallets
    """
    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    if wallet.wallet_type == WalletType.FIAT:
        # For fiat wallets, return stored balance
        return {
            "wallet_id": wallet.id,
            "currency_code": wallet.currency_code,
            "balance": str(wallet.balance),
            "wallet_type": "fiat"
        }
    
    # For crypto wallets, fetch live balance
    if wallet.address:
        # Determine network based on currency
        network_map = {
            "ETH": "mainnet",
            "MATIC": "polygon",
        }
        network = network_map.get(wallet.currency_code, "mainnet")
        
        balance_info = get_wallet_balance(wallet.address, network)
        
        return {
            "wallet_id": wallet.id,
            "currency_code": wallet.currency_code,
            "address": wallet.address,
            "balance_database": str(wallet.balance),
            "balance_blockchain": balance_info.get("balance_eth", "0"),
            "network": network,
            "wallet_type": "crypto"
        }
    
    return {
        "wallet_id": wallet.id,
        "error": "No address found for this wallet"
    }


@router.delete("/{wallet_id}")
async def delete_wallet(
    wallet_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a wallet (only if balance is 0)
    """
    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )
    
    if wallet.balance > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete wallet with non-zero balance"
        )
    
    db.delete(wallet)
    db.commit()
    
    return {"message": "Wallet deleted successfully"}
