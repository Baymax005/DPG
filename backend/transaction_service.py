"""
Transaction Service
Handles deposits, withdrawals, transfers, and balance updates
"""
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Optional
from datetime import datetime

from models import Wallet, Transaction, TransactionType, TransactionStatus
from wallet_service import get_wallet_balance


class TransactionService:
    """Service for handling wallet transactions"""
    
    @staticmethod
    def deposit(
        db: Session,
        wallet_id: str,
        amount: Decimal,
        description: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> Transaction:
        """
        Deposit funds into a wallet
        
        Args:
            db: Database session
            wallet_id: Target wallet ID
            amount: Amount to deposit
            description: Optional description
            reference_id: External reference (e.g., Stripe payment ID)
            
        Returns:
            Transaction object
        """
        # Get wallet
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise ValueError("Wallet not found")
        
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        # Create transaction
        transaction = Transaction(
            wallet_id=wallet_id,
            type=TransactionType.DEPOSIT,
            amount=amount,
            fee=0,  # No fee for deposits initially
            status=TransactionStatus.COMPLETED,
            description=description or f"Deposit to {wallet.currency_code} wallet",
            reference_id=reference_id,
            completed_at=datetime.utcnow()
        )
        
        # Update wallet balance
        wallet.balance += amount
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return transaction
    
    @staticmethod
    def withdraw(
        db: Session,
        wallet_id: str,
        amount: Decimal,
        fee: Decimal = Decimal('0'),
        description: Optional[str] = None,
        tx_hash: Optional[str] = None
    ) -> Transaction:
        """
        Withdraw funds from a wallet
        
        Args:
            db: Database session
            wallet_id: Source wallet ID
            amount: Amount to withdraw
            fee: Transaction fee
            description: Optional description
            tx_hash: Blockchain transaction hash (for crypto)
            
        Returns:
            Transaction object
        """
        # Get wallet
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise ValueError("Wallet not found")
        
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        total_amount = amount + fee
        
        if wallet.balance < total_amount:
            raise ValueError(f"Insufficient balance. Available: {wallet.balance}, Required: {total_amount}")
        
        # Create transaction
        transaction = Transaction(
            wallet_id=wallet_id,
            type=TransactionType.WITHDRAWAL,
            amount=amount,
            fee=fee,
            status=TransactionStatus.COMPLETED,
            description=description or f"Withdrawal from {wallet.currency_code} wallet",
            tx_hash=tx_hash,
            completed_at=datetime.utcnow()
        )
        
        # Update wallet balance
        wallet.balance -= total_amount
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return transaction
    
    @staticmethod
    def transfer(
        db: Session,
        from_wallet_id: str,
        to_wallet_id: str,
        amount: Decimal,
        fee: Decimal = Decimal('0'),
        description: Optional[str] = None
    ) -> tuple[Transaction, Transaction]:
        """
        Transfer funds between two wallets
        
        Args:
            db: Database session
            from_wallet_id: Source wallet ID
            to_wallet_id: Destination wallet ID
            amount: Amount to transfer
            fee: Transaction fee
            description: Optional description
            
        Returns:
            Tuple of (withdrawal_tx, deposit_tx)
        """
        # Get wallets
        from_wallet = db.query(Wallet).filter(Wallet.id == from_wallet_id).first()
        to_wallet = db.query(Wallet).filter(Wallet.id == to_wallet_id).first()
        
        if not from_wallet or not to_wallet:
            raise ValueError("Wallet not found")
        
        if from_wallet_id == to_wallet_id:
            raise ValueError("Cannot transfer to same wallet")
        
        if from_wallet.currency_code != to_wallet.currency_code:
            raise ValueError("Currency mismatch. Use conversion endpoint instead")
        
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        
        total_amount = amount + fee
        
        if from_wallet.balance < total_amount:
            raise ValueError(f"Insufficient balance. Available: {from_wallet.balance}, Required: {total_amount}")
        
        # Create withdrawal transaction
        withdrawal = Transaction(
            wallet_id=from_wallet_id,
            type=TransactionType.TRANSFER,
            amount=amount,
            fee=fee,
            status=TransactionStatus.COMPLETED,
            description=description or f"Transfer to {to_wallet.currency_code} wallet",
            completed_at=datetime.utcnow()
        )
        
        # Create deposit transaction
        deposit = Transaction(
            wallet_id=to_wallet_id,
            type=TransactionType.TRANSFER,
            amount=amount,
            fee=0,
            status=TransactionStatus.COMPLETED,
            description=description or f"Transfer from {from_wallet.currency_code} wallet",
            completed_at=datetime.utcnow()
        )
        
        # Update balances
        from_wallet.balance -= total_amount
        to_wallet.balance += amount
        
        db.add(withdrawal)
        db.add(deposit)
        db.commit()
        db.refresh(withdrawal)
        db.refresh(deposit)
        
        return (withdrawal, deposit)
    
    @staticmethod
    def get_wallet_transactions(
        db: Session,
        wallet_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list[Transaction]:
        """
        Get transaction history for a wallet
        
        Args:
            db: Database session
            wallet_id: Wallet ID
            limit: Number of transactions to return
            offset: Offset for pagination
            
        Returns:
            List of transactions
        """
        transactions = db.query(Transaction).filter(
            Transaction.wallet_id == wallet_id
        ).order_by(
            Transaction.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        return transactions
    
    @staticmethod
    def get_user_all_transactions(
        db: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> list[Transaction]:
        """
        Get all transactions for a user (across all wallets)
        
        Args:
            db: Database session
            user_id: User ID
            limit: Number of transactions to return
            offset: Offset for pagination
            
        Returns:
            List of transactions
        """
        transactions = db.query(Transaction).join(
            Wallet, Transaction.wallet_id == Wallet.id
        ).filter(
            Wallet.user_id == user_id
        ).order_by(
            Transaction.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        return transactions
