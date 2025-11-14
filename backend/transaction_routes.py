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
import logging

logger = logging.getLogger(__name__)
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
    - **network**: Blockchain network (sepolia, amoy, ethereum, polygon)
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
    
    # Check for pending transactions from this wallet (cooldown check)
    from models import Transaction, TransactionStatus
    from datetime import datetime, timedelta
    
    pending_tx = db.query(Transaction).filter(
        Transaction.wallet_id == send_data.wallet_id,
        Transaction.status == TransactionStatus.PENDING,
        Transaction.tx_hash.isnot(None)  # Only check blockchain transactions
    ).first()
    
    if pending_tx:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"⏳ You have a pending transaction. Please wait 10-15 seconds for it to confirm before sending another. Check status: https://sepolia.etherscan.io/tx/{pending_tx.tx_hash}"
        )
    
    # Check wallet balance
    amount = Decimal(str(send_data.amount))
    if wallet.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Available: {wallet.balance}, Required: {amount}"
        )
    
    try:
        # Validate recipient address first
        if not send_data.to_address:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recipient address is required"
            )
        
        # Get blockchain service for the specified network
        blockchain = get_blockchain_service(send_data.network)
        
        # Validate address format
        if not blockchain.is_valid_address(send_data.to_address):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Ethereum address: {send_data.to_address}. Please check the address and try again."
            )
        
        # Check if wallet has blockchain address and private key
        if not wallet.address or not wallet.private_key_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This wallet doesn't have a blockchain address. Please create a crypto wallet first."
            )
        
        # Decrypt user's private key
        from wallet_service import decrypt_private_key
        try:
            private_key = decrypt_private_key(wallet.private_key_encrypted)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to decrypt wallet key: {str(e)}"
            )
        
        # Get wallet's actual blockchain balance
        try:
            blockchain_balance = blockchain.get_balance(wallet.address)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch balance from blockchain: {str(e)}"
            )
        
        # Estimate gas fee first
        try:
            gas_estimate = blockchain.estimate_gas_fee(
                from_address=wallet.address,
                to_address=send_data.to_address,
                amount=amount
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to estimate gas: {str(e)}"
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
            network=send_data.network,  # Save network for status checking
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


@router.get("/status/{tx_hash}")
async def check_transaction_status(
    tx_hash: str,
    network: str = "sepolia",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check blockchain transaction status
    
    - **tx_hash**: Transaction hash to check
    - **network**: Blockchain network (sepolia, ethereum, polygon, amoy)
    
    Returns real-time status from blockchain explorer
    """
    try:
        # Verify transaction belongs to user
        from models import Transaction
        transaction = db.query(Transaction).filter(
            Transaction.tx_hash == tx_hash
        ).first()
        
        if transaction:
            # Verify wallet belongs to user
            wallet = db.query(Wallet).filter(
                Wallet.id == transaction.wallet_id,
                Wallet.user_id == current_user.id
            ).first()
            
            if not wallet:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view this transaction"
                )
        
        # Get blockchain service
        blockchain = get_blockchain_service(network)
        
        # Check status on blockchain
        status_info = blockchain.get_transaction_status(tx_hash)
        
        # Update database if status changed
        if transaction and status_info['status'] != 'pending':
            from models import TransactionStatus
            if status_info['status'] == 'confirmed':
                transaction.status = TransactionStatus.COMPLETED
            elif status_info['status'] == 'failed':
                transaction.status = TransactionStatus.FAILED
            db.commit()
        
        return {
            "tx_hash": tx_hash,
            "status": status_info['status'],
            "confirmations": status_info.get('confirmations', 0),
            "block_number": status_info.get('block_number'),
            "explorer_url": f"{blockchain.network_config['explorer']}/tx/{tx_hash}",
            "network": network
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking transaction status: {str(e)}"
        )


@router.post("/sync-balance/{wallet_id}")
async def sync_wallet_balance(
    wallet_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync wallet balance with blockchain
    
    - **wallet_id**: Wallet ID to sync
    
    Fetches real balance from blockchain and updates database
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
    
    if not wallet.address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This wallet doesn't have a blockchain address"
        )
    
    try:
        # Get blockchain service (default to sepolia for now)
        blockchain = get_blockchain_service('sepolia')
        
        # Get real balance from blockchain
        blockchain_balance = blockchain.get_balance(wallet.address)
        
        # Store old balance for comparison
        old_balance = wallet.balance
        
        # Update database balance
        wallet.balance = blockchain_balance
        db.commit()
        db.refresh(wallet)
        
        return {
            "message": "✅ Balance synced with blockchain",
            "wallet_id": wallet_id,
            "address": wallet.address,
            "old_balance": str(old_balance),
            "new_balance": str(blockchain_balance),
            "difference": str(blockchain_balance - old_balance),
            "network": "sepolia"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing balance: {str(e)}"
        )


@router.delete("/cleanup-deposits")
async def cleanup_incorrect_deposits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Emergency cleanup: Delete auto-generated deposit transactions without tx_hash
    
    This removes incorrect deposit records that were auto-created by the monitor.
    Only deletes deposits that don't have a blockchain transaction hash.
    """
    try:
        from models import Transaction, TransactionType
        
        # Find all deposit transactions without tx_hash (auto-generated ones)
        auto_deposits = db.query(Transaction).filter(
            Transaction.type == TransactionType.DEPOSIT,
            Transaction.tx_hash == None,
            Transaction.wallet_id.in_(
                db.query(Wallet.id).filter(Wallet.user_id == current_user.id)
            )
        ).all()
        
        count = len(auto_deposits)
        
        if count == 0:
            return {
                "message": "No auto-generated deposits found",
                "deleted_count": 0
            }
        
        # Delete them
        for tx in auto_deposits:
            db.delete(tx)
        
        db.commit()
        
        return {
            "message": f"✅ Cleaned up {count} incorrect deposit transaction(s)",
            "deleted_count": count,
            "note": "Real incoming transactions are tracked when you receive funds"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during cleanup: {str(e)}"
        )


@router.post("/scan-deposits/{wallet_id}")
async def scan_for_deposits(
    wallet_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Scan blockchain for incoming deposits using Etherscan API
    
    This fetches REAL transaction history from Etherscan and creates
    deposit records for any incoming transactions we haven't tracked yet.
    """
    logger.info(f"🔍 Starting deposit scan for wallet {wallet_id}")
    try:
        from models import Transaction, TransactionType, TransactionStatus
        from etherscan_service import get_etherscan_service
        import os
        
        # Get wallet
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
                detail="Wallet doesn't have a blockchain address"
            )
        
        # Get network
        network_map = {
            "ETH": "sepolia",
            "MATIC": "amoy"
        }
        network = network_map.get(wallet.currency_code, "sepolia")
        
        # For Amoy/MATIC, use TransactionScanner instead of Etherscan
        if network == "amoy":
            logger.info(f"🟣 Using TransactionScanner for Amoy/MATIC deposits")
            from transaction_scanner import TransactionScanner
            
            scanner = TransactionScanner(network='amoy')
            
            # Get the last block we scanned (or start from recent blocks)
            last_tx = db.query(Transaction).filter(
                Transaction.wallet_id == wallet_id,
                Transaction.type == TransactionType.DEPOSIT,
                Transaction.tx_hash.isnot(None)
            ).order_by(Transaction.created_at.desc()).first()
            
            from_block = 0  # Will scan last 10000 blocks by default
            if last_tx and hasattr(last_tx, 'block_number') and last_tx.block_number:
                from_block = int(last_tx.block_number) + 1
            
            # Scan blockchain for incoming transactions
            logger.info(f"🔎 Scanning Amoy blockchain for MATIC deposits to {wallet.address[:10]}...")
            deposits = scanner.get_incoming_transactions(wallet.address, from_block=from_block)
            logger.info(f"📊 Found {len(deposits)} MATIC deposits from blockchain")
            
            if not deposits:
                return {
                    "message": "📭 No incoming MATIC deposits found on Amoy blockchain",
                    "deposits_found": 0
                }
            
            # Check which deposits we already have
            existing_hashes = set(
                tx.tx_hash for tx in db.query(Transaction).filter(
                    Transaction.wallet_id == wallet_id,
                    Transaction.tx_hash.isnot(None)
                ).all()
            )
            
            new_deposits = []
            for deposit in deposits:
                if deposit['tx_hash'] not in existing_hashes:
                    # Create transaction record
                    tx = Transaction(
                        wallet_id=wallet_id,
                        type=TransactionType.DEPOSIT,
                        amount=float(deposit['amount']),
                        currency_code='MATIC',
                        status=TransactionStatus.COMPLETED,
                        tx_hash=deposit['tx_hash'],
                        description=f"MATIC deposit from {deposit['from_address'][:10]}...",
                        network='amoy'
                    )
                    db.add(tx)
                    
                    # Update wallet balance
                    wallet.balance += Decimal(str(deposit['amount']))
                    
                    new_deposits.append({
                        'amount': str(deposit['amount']),
                        'tx_hash': deposit['tx_hash'],
                        'from': deposit['from_address']
                    })
                    
                    logger.info(f"✅ Added MATIC deposit: {deposit['amount']} MATIC (tx: {deposit['tx_hash'][:10]}...)")
            
            if new_deposits:
                db.commit()
                logger.info(f"💾 Saved {len(new_deposits)} new MATIC deposits to database")
            
            return {
                "message": f"✅ Scan complete! Found {len(new_deposits)} new MATIC deposits",
                "deposits_found": len(new_deposits),
                "new_deposits": new_deposits,
                "network": "amoy"
            }
        
        # Get Etherscan service with API key from environment
        api_key = os.getenv('ETHERSCAN_API_KEY')
        logger.info(f"📡 Using Etherscan API key: {api_key[:10]}..." if api_key else "⚠️ No API key found!")
        
        etherscan = get_etherscan_service(api_key=api_key, network=network)
        
        # Fetch incoming deposits from Etherscan
        logger.info(f"🔎 Scanning blockchain for deposits to {wallet.address[:10]}...")
        deposits = etherscan.get_latest_incoming_deposits(wallet.address)
        logger.info(f"📊 Found {len(deposits)} deposits from Etherscan")
        
        if not deposits:
            return {
                "message": "📭 No incoming deposits found on blockchain",
                "deposits_found": 0
            }
        
        # Check which deposits we already have
        existing_hashes = set(
            tx.tx_hash for tx in db.query(Transaction).filter(
                Transaction.wallet_id == wallet_id,
                Transaction.tx_hash.isnot(None)
            ).all()
        )
        
        new_deposits = []
        for deposit in deposits:
            if deposit['tx_hash'] not in existing_hashes:
                # Create new deposit transaction
                new_tx = Transaction(
                    wallet_id=wallet_id,
                    type=TransactionType.DEPOSIT,
                    amount=deposit['amount'],
                    fee=Decimal('0'),  # No fee for receiving
                    status=TransactionStatus.COMPLETED,
                    tx_hash=deposit['tx_hash'],
                    network=network,
                    description=f"Deposit from {deposit['from_address'][:10]}...",
                    completed_at=deposit['timestamp']
                )
                db.add(new_tx)
                new_deposits.append(deposit)
        
        if new_deposits:
            db.commit()
            
            # Update wallet balance from blockchain
            blockchain = get_blockchain_service(network)
            wallet.balance = blockchain.get_balance(wallet.address)
            db.commit()
            
            total_amount = sum(d['amount'] for d in new_deposits)
            
            return {
                "message": f"✅ Found {len(new_deposits)} new deposit(s)!",
                "deposits_found": len(new_deposits),
                "total_amount": str(total_amount),
                "currency": wallet.currency_code,
                "new_balance": str(wallet.balance),
                "deposits": [
                    {
                        "amount": str(d['amount']),
                        "from": d['from_address'],
                        "tx_hash": d['tx_hash'],
                        "date": d['timestamp'].isoformat()
                    }
                    for d in new_deposits
                ]
            }
        else:
            return {
                "message": "✅ All deposits already tracked",
                "deposits_found": 0,
                "note": "No new deposits to add"
            }
        
    except Exception as e:
        db.rollback()
        import traceback
        logger.error(f"Error scanning deposits: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scanning for deposits: {str(e)}"
        )

