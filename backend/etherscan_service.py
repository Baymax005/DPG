"""
Etherscan API Service
Fetches real transaction history from Etherscan for Ethereum addresses
"""
import requests
import logging
from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EtherscanService:
    """Service to interact with Etherscan API"""
    
    def __init__(self, api_key: str, network: str = "sepolia"):
        """
        Initialize Etherscan service
        
        Args:
            api_key: Etherscan API key
            network: Network name (mainnet, sepolia, goerli, etc.)
        """
        self.api_key = api_key
        self.network = network
        
        # V2 API - single unified endpoint for all chains
        self.base_url = "https://api.etherscan.io/v2/api"
        
        # Chain IDs for different networks
        self.chain_ids = {
            "mainnet": "1",
            "sepolia": "11155111",
            "holesky": "17000",
        }
        
        self.chain_id = self.chain_ids.get(network, self.chain_ids["sepolia"])
    
    def get_normal_transactions(self, address: str, startblock: int = 0, endblock: int = 99999999) -> List[Dict]:
        """
        Get list of normal transactions for an address
        
        Args:
            address: Ethereum address to query
            startblock: Starting block number (default 0)
            endblock: Ending block number (default 99999999 for latest)
            
        Returns:
            List of transaction dictionaries
        """
        try:
            params = {
                "chainid": self.chain_id,  # V2 requires chainid
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": startblock,
                "endblock": endblock,
                "page": 1,
                "offset": 100,  # Get last 100 transactions
                "sort": "desc",  # Most recent first
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if data["status"] == "1" and data["message"] == "OK":
                transactions = data["result"]
                logger.info(f"✅ Found {len(transactions)} transactions for {address[:10]}...")
                return transactions
            elif data["message"] == "No transactions found":
                logger.info(f"📭 No transactions found for {address[:10]}...")
                return []
            else:
                logger.error(f"❌ Etherscan API error: {data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching transactions from Etherscan: {e}")
            return []
    
    def get_incoming_transactions(self, address: str, startblock: int = 0) -> List[Dict]:
        """
        Get only incoming transactions (where address is the recipient)
        
        Args:
            address: Ethereum address to query
            startblock: Starting block number
            
        Returns:
            List of incoming transaction dictionaries
        """
        all_txs = self.get_normal_transactions(address, startblock)
        
        # Filter for incoming transactions (where 'to' address matches)
        incoming = [
            tx for tx in all_txs 
            if tx.get('to', '').lower() == address.lower() and tx.get('isError') == '0'
        ]
        
        logger.info(f"💰 Found {len(incoming)} incoming transactions for {address[:10]}...")
        return incoming
    
    def parse_transaction(self, tx: Dict) -> Dict:
        """
        Parse Etherscan transaction into our format
        
        Args:
            tx: Raw transaction from Etherscan
            
        Returns:
            Parsed transaction dictionary
        """
        # Convert wei to ETH (divide by 10^18)
        amount_wei = int(tx.get('value', '0'))
        amount_eth = Decimal(amount_wei) / Decimal(10**18)
        
        # Convert timestamp to datetime
        timestamp = int(tx.get('timeStamp', '0'))
        tx_date = datetime.fromtimestamp(timestamp)
        
        return {
            'tx_hash': tx.get('hash'),
            'from_address': tx.get('from'),
            'to_address': tx.get('to'),
            'amount': amount_eth,
            'block_number': int(tx.get('blockNumber', '0')),
            'timestamp': tx_date,
            'gas_used': int(tx.get('gasUsed', '0')),
            'gas_price': int(tx.get('gasPrice', '0')),
            'is_error': tx.get('isError') == '1',
            'confirmations': int(tx.get('confirmations', '0'))
        }
    
    def get_latest_incoming_deposits(self, address: str, since_block: int = 0) -> List[Dict]:
        """
        Get latest incoming deposits with parsed data
        
        Args:
            address: Ethereum address
            since_block: Only get transactions after this block
            
        Returns:
            List of parsed incoming transactions
        """
        incoming = self.get_incoming_transactions(address, since_block)
        parsed = [self.parse_transaction(tx) for tx in incoming]
        
        # Filter out zero-value transactions
        non_zero = [tx for tx in parsed if tx['amount'] > 0]
        
        return non_zero


# Global instance
_etherscan_service = None


def get_etherscan_service(api_key: str = None, network: str = "sepolia") -> EtherscanService:
    """Get or create Etherscan service singleton"""
    global _etherscan_service
    
    if _etherscan_service is None or api_key is not None:
        if api_key is None:
            # Try to get from environment
            import os
            api_key = os.getenv('ETHERSCAN_API_KEY', '')
        
        _etherscan_service = EtherscanService(api_key, network)
    
    return _etherscan_service


if __name__ == "__main__":
    """Test the service"""
    # Test with a known address
    service = EtherscanService("XEUGFHET25SI6JJ3GQ1C3VYZ41VH1AE7EY", "sepolia")
    
    # Example address
    test_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    
    print(f"Fetching transactions for {test_address}...")
    deposits = service.get_latest_incoming_deposits(test_address)
    
    print(f"\nFound {len(deposits)} incoming deposits:")
    for deposit in deposits:
        print(f"  💰 {deposit['amount']} ETH from {deposit['from_address'][:10]}...")
        print(f"     TX: {deposit['tx_hash'][:20]}...")
        print(f"     Date: {deposit['timestamp']}")
