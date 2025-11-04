"""
Transaction Monitor
Background service to monitor pending blockchain transactions and update their status
"""
import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Transaction, TransactionStatus
from blockchain_service import get_blockchain_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransactionMonitor:
    """Monitor and update pending transaction statuses"""
    
    def __init__(self, check_interval: int = 30):
        """
        Initialize monitor
        
        Args:
            check_interval: Seconds between checks (default 30)
        """
        self.check_interval = check_interval
        self.running = False
    
    async def start(self):
        """Start monitoring loop"""
        self.running = True
        logger.info("🔍 Transaction monitor started")
        
        while self.running:
            try:
                await self.check_pending_transactions()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Error in transaction monitor: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def check_pending_transactions(self):
        """Check all pending transactions and update their status"""
        db: Session = SessionLocal()
        
        try:
            # Get all pending transactions with tx_hash
            pending_txs = db.query(Transaction).filter(
                Transaction.status == TransactionStatus.PENDING,
                Transaction.tx_hash.isnot(None)
            ).all()
            
            if pending_txs:
                logger.info(f"📋 Checking {len(pending_txs)} pending transaction(s)")
                
                for tx in pending_txs:
                    try:
                        # Get network from transaction (default to sepolia)
                        network = tx.network or 'sepolia'
                        
                        # Get blockchain service
                        blockchain = get_blockchain_service(network)
                        
                        # Check transaction status on blockchain
                        status_info = blockchain.get_transaction_status(tx.tx_hash)
                        
                        # Update if status changed
                        if status_info['status'] == 'confirmed':
                            tx.status = TransactionStatus.COMPLETED
                            tx.completed_at = datetime.utcnow()
                            logger.info(f"✅ Transaction {tx.tx_hash[:10]}... confirmed!")
                            
                        elif status_info['status'] == 'failed':
                            tx.status = TransactionStatus.FAILED
                            tx.completed_at = datetime.utcnow()
                            logger.warning(f"❌ Transaction {tx.tx_hash[:10]}... failed")
                        
                        # Still pending - log confirmations
                        elif status_info['status'] == 'pending':
                            logger.debug(f"⏳ Transaction {tx.tx_hash[:10]}... still pending")
                        
                    except Exception as e:
                        logger.error(f"❌ Error checking tx {tx.tx_hash}: {e}")
                        continue
            
            # Also check for incoming transactions to our wallets
            await self.check_incoming_transactions(db)
            
            # Commit all changes
            db.commit()
            
        except Exception as e:
            logger.error(f"❌ Error in check_pending_transactions: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def check_incoming_transactions(self, db: Session):
        """Check for incoming transactions to wallet addresses"""
        try:
            from models import Wallet, TransactionType
            from decimal import Decimal
            
            # Get all crypto wallets with addresses
            wallets = db.query(Wallet).filter(
                Wallet.address.isnot(None)
            ).all()
            
            for wallet in wallets:
                try:
                    # Determine network from currency
                    network_map = {
                        "ETH": "sepolia",
                        "MATIC": "mumbai"
                    }
                    network = network_map.get(wallet.currency_code, "sepolia")
                    
                    # Get blockchain service
                    blockchain = get_blockchain_service(network)
                    
                    # Get current balance from blockchain
                    current_blockchain_balance = blockchain.get_balance(wallet.address)
                    
                    # Calculate total deposits and withdrawals from transaction history
                    total_deposits = Decimal('0')
                    total_withdrawals = Decimal('0')
                    
                    wallet_transactions = db.query(Transaction).filter(
                        Transaction.wallet_id == wallet.id
                    ).all()
                    
                    for tx in wallet_transactions:
                        if tx.type == TransactionType.DEPOSIT:
                            total_deposits += tx.amount
                        elif tx.type == TransactionType.WITHDRAWAL:
                            total_withdrawals += (tx.amount + tx.fee)
                    
                    # Expected balance = deposits - withdrawals
                    expected_balance = total_deposits - total_withdrawals
                    
                    # If blockchain balance > expected balance, we missed a deposit!
                    if current_blockchain_balance > expected_balance:
                        missed_deposit = current_blockchain_balance - expected_balance
                        
                        # Only create deposit if amount is significant (> 0.000001)
                        if missed_deposit > Decimal('0.000001'):
                            logger.info(f"💰 Detected incoming deposit to {wallet.currency_code} wallet!")
                            logger.info(f"   Address: {wallet.address[:10]}...")
                            logger.info(f"   Amount: +{missed_deposit} {wallet.currency_code}")
                            logger.info(f"   Blockchain: {current_blockchain_balance}, Expected: {expected_balance}")
                            
                            # Create deposit transaction record
                            new_tx = Transaction(
                                wallet_id=wallet.id,
                                type=TransactionType.DEPOSIT,
                                amount=Decimal(str(missed_deposit)),
                                status=TransactionStatus.COMPLETED,
                                description=f"Incoming {wallet.currency_code} deposit",
                                network=network,
                                completed_at=datetime.utcnow()
                            )
                            db.add(new_tx)
                            
                            logger.info(f"✅ Created deposit transaction record for +{missed_deposit} {wallet.currency_code}")
                    
                    # Always sync wallet balance to blockchain
                    if wallet.balance != current_blockchain_balance:
                        wallet.balance = current_blockchain_balance
                        
                except Exception as e:
                    logger.error(f"❌ Error checking incoming for wallet {wallet.id}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error in check_incoming_transactions: {e}")
    
    def stop(self):
        """Stop monitoring loop"""
        self.running = False
        logger.info("🛑 Transaction monitor stopped")


# Global monitor instance
_monitor = None


def get_transaction_monitor() -> TransactionMonitor:
    """Get or create transaction monitor singleton"""
    global _monitor
    if _monitor is None:
        _monitor = TransactionMonitor(check_interval=10)  # Check every 10 seconds
    return _monitor


async def start_transaction_monitor():
    """Start the transaction monitor (called on app startup)"""
    monitor = get_transaction_monitor()
    await monitor.start()


def stop_transaction_monitor():
    """Stop the transaction monitor (called on app shutdown)"""
    monitor = get_transaction_monitor()
    monitor.stop()


if __name__ == "__main__":
    """Test the monitor"""
    async def test():
        monitor = TransactionMonitor(check_interval=10)
        await monitor.start()
    
    asyncio.run(test())
