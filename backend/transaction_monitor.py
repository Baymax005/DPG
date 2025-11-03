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
            
            if not pending_txs:
                logger.debug("No pending transactions to check")
                return
            
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
            
            # Commit all changes
            db.commit()
            
        except Exception as e:
            logger.error(f"❌ Error in check_pending_transactions: {e}")
            db.rollback()
        finally:
            db.close()
    
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
