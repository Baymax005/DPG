"""
Transaction Routes
Handles deposits, withdrawals, transfers, and transaction history
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from database import get_db
from models import User, Wallet
from schemas import (
    DepositRequest, WithdrawalRequest, TransferRequest, SendRequest,
    TransactionResponse, SuccessResponse
)
from auth_routes import get_current_user
from transaction_service import TransactionService
from blockchain_service import get_blockchain_service
import os

router = APIRouter(prefix="/api/v1/transactions", tags=["Transactions"])


@router.post("/deposit", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def deposit_funds(
    deposit_data: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deposit funds into a wallet
    
    - **wallet_id**: Target wallet ID
    - **amount**: Amount to deposit
    - **description**: Optional description
    - **reference_id**: External payment reference (e.g., Stripe payment ID)
    """
    # Verify wallet belongs to user
    wallet = db.query(Wallet).filter(
        Wallet.id == deposit_data.wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found or does not belong to you"
        )
    
    try:
        transaction = TransactionService.deposit(
            db=db,
            wallet_id=deposit_data.wallet_id,
            amount=Decimal(str(deposit_data.amount)),
            description=deposit_data.description,
            reference_id=deposit_data.reference_id
        )
        
        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/withdraw", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def withdraw_funds(
    withdrawal_data: WithdrawalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Withdraw funds from a wallet
    
    - **wallet_id**: Source wallet ID
    - **amount**: Amount to withdraw
    - **description**: Optional description
    - **destination_address**: Crypto address for withdrawals (optional)
    """
    # Verify wallet belongs to user
    wallet = db.query(Wallet).filter(
        Wallet.id == withdrawal_data.wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found or does not belong to you"
        )
    
    try:
        # Calculate fee (0.5% for crypto, 0 for fiat initially)
        amount = Decimal(str(withdrawal_data.amount))
        fee = Decimal('0')
        
        if wallet.wallet_type.value == "crypto":
            fee = amount * Decimal('0.005')  # 0.5% fee
        
        transaction = TransactionService.withdraw(
            db=db,
            wallet_id=withdrawal_data.wallet_id,
            amount=amount,
            fee=fee,
            description=withdrawal_data.description
        )
        
        return transaction
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/transfer", status_code=status.HTTP_201_CREATED)
async def transfer_funds(
    transfer_data: TransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Transfer funds between wallets
    
    - **from_wallet_id**: Source wallet ID
    - **to_wallet_id**: Destination wallet ID
    - **amount**: Amount to transfer
    - **description**: Optional description
    """
    # Verify source wallet belongs to user
    from_wallet = db.query(Wallet).filter(
        Wallet.id == transfer_data.from_wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not from_wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source wallet not found or does not belong to you"
        )
    
    # Verify destination wallet exists
    to_wallet = db.query(Wallet).filter(
        Wallet.id == transfer_data.to_wallet_id
    ).first()
    
    if not to_wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination wallet not found"
        )
    
    try:
        # No fee for internal transfers (industry standard)
        amount = Decimal(str(transfer_data.amount))
        fee = Decimal('0')  # FREE internal transfers
        
        withdrawal_tx, deposit_tx = TransactionService.transfer(
            db=db,
            from_wallet_id=transfer_data.from_wallet_id,
            to_wallet_id=transfer_data.to_wallet_id,
            amount=amount,
            fee=fee,
            description=transfer_data.description
        )
        
        return {
            "message": "Transfer successful",
            "withdrawal_transaction": {
                "id": withdrawal_tx.id,
                "amount": str(withdrawal_tx.amount),
                "fee": str(withdrawal_tx.fee),
                "status": withdrawal_tx.status.value
            },
            "deposit_transaction": {
                "id": deposit_tx.id,
                "amount": str(deposit_tx.amount),
                "status": deposit_tx.status.value
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/send", status_code=status.HTTP_201_CREATED)
async def send_to_address(
    send_data: SendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send funds to external blockchain address
    
    - **wallet_id**: Source wallet ID
    - **to_address**: Destination blockchain address
    - **amount**: Amount to send
    - **network**: Blockchain network (sepolia, mumbai, ethereum, polygon)
    - **description**: Optional description
    
    ⚠️ This sends REAL blockchain transactions on testnet/mainnet
    """
    # Verify wallet belongs to user
    wallet = db.query(Wallet).filter(
        Wallet.id == send_data.wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found or does not belong to you"
        )
    
    # Check wallet balance
    amount = Decimal(str(send_data.amount))
    if wallet.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Available: {wallet.balance}, Required: {amount}"
        )
    
    try:
        # Get blockchain service for the specified network
        blockchain = get_blockchain_service(send_data.network)
        
        # Check if wallet has blockchain address and private key
        if not wallet.address or not wallet.private_key_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This wallet doesn't have a blockchain address. Please create a crypto wallet first."
            )
        
        # Decrypt user's private key
        from wallet_service import decrypt_private_key
        private_key = decrypt_private_key(wallet.private_key_encrypted)
        
        # Get wallet's actual blockchain balance
        blockchain_balance = blockchain.get_balance(wallet.address)
        
        # Estimate gas fee first
        gas_estimate = blockchain.estimate_gas_fee(
            from_address=wallet.address,
            to_address=send_data.to_address,
            amount=amount
        )
        
        # Check if user has enough ETH for amount + gas
        total_needed = amount + Decimal(gas_estimate['total_fee_eth'])
        if blockchain_balance < total_needed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient blockchain balance. You have {blockchain_balance} ETH but need {total_needed} ETH (including gas fee of {gas_estimate['total_fee_eth']} ETH). Please deposit testnet ETH first."
            )
        
        # Send blockchain transaction using USER's wallet
        tx_result = blockchain.send_transaction(
            private_key=private_key,
            to_address=send_data.to_address,
            amount=amount
        )
        
        # Create transaction record in database
        from models import Transaction, TransactionType, TransactionStatus
        from datetime import datetime
        
        transaction = Transaction(
            wallet_id=send_data.wallet_id,
            type=TransactionType.WITHDRAWAL,
            amount=amount,
            fee=Decimal(gas_estimate['total_fee_eth']),
            status=TransactionStatus.PENDING,
            description=send_data.description or f"Send to {send_data.to_address[:10]}...",
            tx_hash=tx_result['tx_hash'],
            created_at=datetime.utcnow()
        )
        
        # Update database balance to match blockchain (sync)
        wallet.balance = blockchain_balance - total_needed
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return {
            "message": "✅ Transaction sent to blockchain!",
            "tx_hash": tx_result['tx_hash'],
            "to_address": send_data.to_address,
            "amount": str(amount),
            "gas_fee": gas_estimate['total_fee_eth'],
            "network": send_data.network,
            "status": "pending",
            "explorer_url": tx_result['explorer_url'],
            "note": "Transaction is pending confirmation. Check Etherscan for status."
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blockchain error: {str(e)}"
        )


@router.get("/wallet/{wallet_id}", response_model=List[TransactionResponse])
async def get_wallet_transactions(
    wallet_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transaction history for a specific wallet
    
    - **wallet_id**: Wallet ID
    - **limit**: Number of transactions to return (default 50)
    - **offset**: Offset for pagination (default 0)
    """
    # Verify wallet belongs to user
    wallet = db.query(Wallet).filter(
        Wallet.id == wallet_id,
        Wallet.user_id == current_user.id
    ).first()
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found or does not belong to you"
        )
    
    transactions = TransactionService.get_wallet_transactions(
        db=db,
        wallet_id=wallet_id,
        limit=limit,
        offset=offset
    )
    
    return transactions


@router.get("/history", response_model=List[TransactionResponse])
async def get_user_transactions(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all transactions for the current user (across all wallets)
    
    - **limit**: Number of transactions to return (default 50)
    - **offset**: Offset for pagination (default 0)
    """
    transactions = TransactionService.get_user_all_transactions(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    return transactions
