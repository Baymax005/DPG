"""
Transaction Scanner using Infura RPC
Scans blockchain for incoming ETH transfers using eth_getLogs
"""
from web3 import Web3
import logging
from typing import List, Dict
from decimal import Decimal
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransactionScanner:
    """Scan blockchain for transactions using Web3/Infura"""
    
    def __init__(self, rpc_url: str = None):
        """Initialize scanner with Web3 provider"""
        if rpc_url is None:
            rpc_url = os.getenv("SEPOLIA_RPC_URL", "https://sepolia.infura.io/v3/01888b56d7994053a61d869173139fb2")
        
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        logger.info(f"🌐 Connected to Web3: {self.w3.is_connected()}")
    
    def get_incoming_transactions(self, address: str, from_block: int = 0, to_block: str = "latest") -> List[Dict]:
        """
        Get incoming transactions for an address using eth_getLogs
        
        Args:
            address: Ethereum address to scan
            from_block: Starting block number
            to_block: Ending block (number or "latest")
            
        Returns:
            List of incoming transaction dictionaries
        """
        try:
            address = Web3.to_checksum_address(address)
            
            # Get current block
            current_block = self.w3.eth.block_number
            logger.info(f"📊 Current block: {current_block}")
            
            # If from_block is 0, start from recent blocks (last 10000)
            if from_block == 0:
                from_block = max(0, current_block - 10000)
            
            logger.info(f"🔍 Scanning blocks {from_block} to {to_block}...")
            
            # Get all blocks in range and check transactions
            incoming_txs = []
            
            # Scan in chunks to avoid timeout
            chunk_size = 1000
            for start in range(from_block, current_block + 1, chunk_size):
                end = min(start + chunk_size - 1, current_block)
                
                logger.info(f"  Scanning chunk {start} to {end}...")
                
                # Get blocks in this range
                for block_num in range(start, end + 1):
                    try:
                        block = self.w3.eth.get_block(block_num, full_transactions=True)
                        
                        # Check each transaction in the block
                        for tx in block.transactions:
                            # Check if this is an incoming transaction
                            if tx.to and tx.to.lower() == address.lower() and tx.value > 0:
                                # Get transaction receipt for status
                                receipt = self.w3.eth.get_transaction_receipt(tx.hash)
                                
                                if receipt.status == 1:  # Successful transaction
                                    incoming_txs.append({
                                        'tx_hash': tx.hash.hex(),
                                        'from_address': tx['from'],
                                        'to_address': tx.to,
                                        'amount': Decimal(tx.value) / Decimal(10**18),
                                        'block_number': tx.blockNumber,
                                        'timestamp': datetime.fromtimestamp(block.timestamp),
                                        'gas_used': receipt.gasUsed,
                                        'gas_price': tx.gasPrice,
                                        'confirmations': current_block - tx.blockNumber
                                    })
                                    
                                    logger.info(f"  💰 Found deposit: {tx.value / 10**18} ETH in block {tx.blockNumber}")
                    
                    except Exception as e:
                        logger.debug(f"Error checking block {block_num}: {e}")
                        continue
            
            logger.info(f"✅ Found {len(incoming_txs)} incoming transactions")
            return incoming_txs
            
        except Exception as e:
            logger.error(f"❌ Error scanning transactions: {e}")
            return []
    
    def get_recent_deposits(self, address: str, blocks_back: int = 10000) -> List[Dict]:
        """
        Get recent deposits (last N blocks)
        
        Args:
            address: Ethereum address
            blocks_back: How many blocks to look back
            
        Returns:
            List of deposit transactions
        """
        current_block = self.w3.eth.block_number
        from_block = max(0, current_block - blocks_back)
        
        return self.get_incoming_transactions(address, from_block=from_block)


# Global instance
_scanner = None


def get_transaction_scanner(rpc_url: str = None) -> TransactionScanner:
    """Get or create transaction scanner singleton"""
    global _scanner
    
    if _scanner is None:
        _scanner = TransactionScanner(rpc_url)
    
    return _scanner


if __name__ == "__main__":
    """Test the scanner"""
    # Test with your wallet
    scanner = TransactionScanner()
    
    test_address = "0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765"
    
    print(f"🔍 Scanning for deposits to {test_address}...")
    print("⏳ This may take a moment...\n")
    
    deposits = scanner.get_recent_deposits(test_address, blocks_back=50000)
    
    print(f"\n✅ Found {len(deposits)} deposits:")
    for dep in deposits:
        print(f"\n  💰 {dep['amount']} ETH")
        print(f"     From: {dep['from_address']}")
        print(f"     TX: {dep['tx_hash']}")
        print(f"     Block: {dep['block_number']}")
        print(f"     Time: {dep['timestamp']}")
