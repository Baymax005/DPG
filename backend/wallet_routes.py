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
    decrypt_private_key,
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


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_wallet(
    import_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import an existing wallet using private key
    
    - **currency_code**: Currency code (ETH, MATIC)
    - **private_key**: The wallet's private key (will be encrypted)
    """
    currency_code = import_data.get('currency_code', '').upper()
    private_key = import_data.get('private_key', '').strip()
    
    if not currency_code or not private_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currency code and private key are required"
        )
    
    # Validate private key format
    if not private_key.startswith('0x') or len(private_key) != 66:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid private key format"
        )
    
    try:
        # Get address from private key
        from eth_account import Account
        account = Account.from_key(private_key)
        public_address = account.address
        
        # Check if wallet with this address already exists
        existing_wallet = db.query(Wallet).filter(
            Wallet.address == public_address
        ).first()
        
        if existing_wallet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This wallet is already imported"
            )
        
        # Check if user already has a wallet for this currency
        existing_currency_wallet = db.query(Wallet).filter(
            Wallet.user_id == current_user.id,
            Wallet.currency_code == currency_code
        ).first()
        
        if existing_currency_wallet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have a {currency_code} wallet. Delete it first or use a different currency."
            )
        
        # Encrypt private key
        encrypted_key = encrypt_private_key(private_key)
        
        # Get blockchain balance
        from blockchain_service import get_blockchain_service
        network_map = {"ETH": "sepolia", "MATIC": "mumbai"}
        network = network_map.get(currency_code, "sepolia")
        blockchain = get_blockchain_service(network)
        balance = blockchain.get_balance(public_address)
        
        # Create wallet record
        new_wallet = Wallet(
            user_id=current_user.id,
            currency_code=currency_code,
            wallet_type=WalletType.CRYPTO,
            balance=balance,
            address=public_address,
            private_key_encrypted=encrypted_key
        )
        
        db.add(new_wallet)
        db.commit()
        db.refresh(new_wallet)
        
        return {
            "message": "Wallet imported successfully",
            "id": new_wallet.id,
            "currency": currency_code,
            "address": public_address,
            "balance": str(balance),
            "network": network
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to import wallet: {str(e)}"
        )


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
    Delete a wallet
    Warning: This will delete all associated transactions as well
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
    
    # Delete all transactions associated with this wallet first
    from models import Transaction
    db.query(Transaction).filter(Transaction.wallet_id == wallet_id).delete()
    
    # Delete the wallet
    db.delete(wallet)
    db.commit()
    
    return {"message": "Wallet deleted successfully"}


@router.post("/{wallet_id}/sync-blockchain")
async def sync_wallet_from_blockchain(
    wallet_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync wallet balance from blockchain
    Updates database balance to match actual blockchain balance
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
    
    if not wallet.address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This wallet doesn't have a blockchain address"
        )
    
    # Get blockchain balance
    from blockchain_service import get_blockchain_service
    
    # Map currency to network
    network_map = {
        "ETH": "sepolia",  # Use testnet for testing
        "MATIC": "mumbai"
    }
    network = network_map.get(wallet.currency_code, "sepolia")
    
    blockchain = get_blockchain_service(network)
    blockchain_balance = blockchain.get_balance(wallet.address)
    
    # Update database balance
    wallet.balance = blockchain_balance
    db.commit()
    
    return {
        "message": "✅ Wallet synced with blockchain",
        "wallet_id": wallet.id,
        "currency": wallet.currency_code,
        "address": wallet.address,
        "balance": str(blockchain_balance),
        "network": network
    }


@router.get("/{wallet_id}/export-private-key")
async def export_wallet_private_key(
    wallet_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export the private key for a wallet
    
    ⚠️ WARNING: This is a sensitive operation!
    Private keys should NEVER be shared and should be stored securely.
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
    
    if not wallet.private_key_encrypted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This wallet doesn't have a private key (fiat wallet or imported without key)"
        )
    
    try:
        # Decrypt the private key
        private_key = decrypt_private_key(wallet.private_key_encrypted)
        
        return {
            "wallet_id": wallet.id,
            "currency": wallet.currency_code,
            "address": wallet.address,
            "private_key": private_key,
            "warning": "⚠️ NEVER share your private key with anyone! Anyone with this key has full control of your wallet."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decrypt private key: {str(e)}"
        )


