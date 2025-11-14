"""
Blockchain Service
Handles blockchain interactions for Ethereum (Sepolia testnet and mainnet)
"""
import os
from decimal import Decimal
from typing import Optional, Dict, Any
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockchainService:
    """Service for interacting with Ethereum blockchain"""
    
    # Network configurations
    NETWORKS = {
        'sepolia': {
            'rpc_url': os.getenv('SEPOLIA_RPC_URL', 'https://sepolia.infura.io/v3/YOUR_INFURA_KEY'),
            'chain_id': 11155111,
            'explorer': 'https://sepolia.etherscan.io',
            'name': 'Sepolia Testnet'
        },
        'ethereum': {
            'rpc_url': os.getenv('ETHEREUM_RPC_URL', 'https://mainnet.infura.io/v3/YOUR_INFURA_KEY'),
            'chain_id': 1,
            'explorer': 'https://etherscan.io',
            'name': 'Ethereum Mainnet'
        },
        'amoy': {
            'rpc_url': os.getenv('AMOY_RPC_URL', 'https://polygon-amoy.infura.io/v3/YOUR_INFURA_KEY'),
            'chain_id': 80002,
            'explorer': 'https://amoy.polygonscan.com',
            'name': 'Polygon Amoy Testnet'
        },
        'polygon': {
            'rpc_url': os.getenv('POLYGON_RPC_URL', 'https://polygon-mainnet.infura.io/v3/YOUR_INFURA_KEY'),
            'chain_id': 137,
            'explorer': 'https://polygonscan.com',
            'name': 'Polygon Mainnet'
        }
    }
    
    def __init__(self, network: str = 'sepolia'):
        """
        Initialize blockchain service
        
        Args:
            network: Network name (sepolia, ethereum, mumbai, polygon)
        """
        if network not in self.NETWORKS:
            raise ValueError(f"Unsupported network: {network}. Supported: {list(self.NETWORKS.keys())}")
        
        self.network = network
        self.network_config = self.NETWORKS[network]
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.network_config['rpc_url']))
        
        # Note: PoA middleware not needed in newer Web3.py versions
        # The library handles this automatically
        
        # Verify connection
        if not self.w3.is_connected():
            logger.error(f"Failed to connect to {self.network_config['name']}")
            raise ConnectionError(f"Cannot connect to {self.network_config['name']}")
        
        logger.info(f"✅ Connected to {self.network_config['name']}")
    
    def get_balance(self, address: str) -> Decimal:
        """
        Get ETH balance of an address
        
        Args:
            address: Ethereum address
            
        Returns:
            Balance in ETH (Decimal)
        """
        try:
            # Convert to proper checksum address
            checksum_address = self.w3.to_checksum_address(address)
            balance_wei = self.w3.eth.get_balance(checksum_address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return Decimal(str(balance_eth))
        except Exception as e:
            logger.error(f"Error getting balance for {address}: {e}")
            raise
    
    def estimate_gas_fee(self, from_address: str, to_address: str, amount: Decimal) -> Dict[str, Any]:
        """
        Estimate gas fee for a transaction
        
        Args:
            from_address: Sender address
            to_address: Recipient address
            amount: Amount in ETH
            
        Returns:
            Dict with gas estimate, gas price, and total fee
        """
        try:
            from_addr = self.w3.to_checksum_address(from_address)
            to_addr = self.w3.to_checksum_address(to_address)
            amount_wei = self.w3.to_wei(amount, 'ether')
            
            # Estimate gas
            gas_estimate = self.w3.eth.estimate_gas({
                'from': from_addr,
                'to': to_addr,
                'value': amount_wei
            })
            
            # Get current gas price
            gas_price = self.w3.eth.gas_price
            
            # Calculate total fee
            total_fee_wei = gas_estimate * gas_price
            total_fee_eth = self.w3.from_wei(total_fee_wei, 'ether')
            
            return {
                'gas_estimate': gas_estimate,
                'gas_price_wei': str(gas_price),
                'gas_price_gwei': str(self.w3.from_wei(gas_price, 'gwei')),
                'total_fee_eth': str(total_fee_eth),
                'total_fee_usd': None  # TODO: Add price oracle
            }
        except Exception as e:
            logger.error(f"Error estimating gas: {e}")
            # Return default estimate
            return {
                'gas_estimate': 21000,
                'gas_price_wei': '0',
                'gas_price_gwei': '0',
                'total_fee_eth': '0',
                'total_fee_usd': None
            }
    
    def send_transaction(
        self,
        private_key: str,
        to_address: str,
        amount: Decimal,
        gas_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send ETH transaction
        
        Args:
            private_key: Sender's private key (hex string)
            to_address: Recipient address
            amount: Amount in ETH
            gas_price: Optional custom gas price (in wei)
            
        Returns:
            Dict with tx_hash and status
        """
        try:
            # Validate to_address first
            if not to_address or not isinstance(to_address, str):
                raise ValueError("Recipient address is required")
            
            if not self.is_valid_address(to_address):
                raise ValueError(f"Invalid Ethereum address: {to_address}")
            
            # Get account from private key
            try:
                account = Account.from_key(private_key)
            except Exception as e:
                logger.error(f"Invalid private key: {e}")
                raise ValueError("Invalid private key format")
            
            from_address = account.address
            
            # Convert addresses to checksum
            from_addr = self.w3.to_checksum_address(from_address)
            to_addr = self.w3.to_checksum_address(to_address)
            
            # Convert amount to wei
            try:
                amount_wei = self.w3.to_wei(amount, 'ether')
            except Exception as e:
                raise ValueError(f"Invalid amount: {amount}")
            
            # Check sender balance
            sender_balance_wei = self.w3.eth.get_balance(from_addr)
            sender_balance_eth = self.w3.from_wei(sender_balance_wei, 'ether')
            
            # Get nonce - use 'pending' to get latest including pending txs
            try:
                nonce = self.w3.eth.get_transaction_count(from_addr, 'pending')
                logger.info(f"📋 Nonce for {from_addr}: {nonce} (including pending)")
            except Exception as e:
                logger.error(f"Failed to get nonce: {e}")
                raise ValueError(f"Failed to connect to blockchain: {str(e)}")
            
            # Get gas price with buffer for faster confirmation
            if gas_price is None:
                try:
                    base_gas_price = self.w3.eth.gas_price
                    # Add 20% buffer for faster confirmation and to avoid "underpriced" errors
                    gas_price = int(base_gas_price * 1.2)
                    logger.info(f"⛽ Gas price: {self.w3.from_wei(gas_price, 'gwei')} gwei (base + 20%)")
                except Exception as e:
                    logger.error(f"Failed to get gas price: {e}")
                    gas_price = self.w3.to_wei(2, 'gwei')  # Fallback to 2 gwei
            
            # Calculate total cost
            gas_cost_wei = 21000 * gas_price
            total_cost_wei = amount_wei + gas_cost_wei
            
            if sender_balance_wei < total_cost_wei:
                raise ValueError(
                    f"Insufficient balance: have {sender_balance_eth} ETH, "
                    f"need {self.w3.from_wei(total_cost_wei, 'ether')} ETH "
                    f"(amount + gas)"
                )
            
            # Build transaction
            transaction = {
                'nonce': nonce,
                'to': to_addr,
                'value': amount_wei,
                'gas': 21000,  # Standard ETH transfer
                'gasPrice': gas_price,
                'chainId': self.network_config['chain_id']
            }
            
            logger.info(f"Building transaction: from={from_addr[:10]}... to={to_addr[:10]}... value={amount} ETH")
            
            # Sign transaction
            try:
                signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            except Exception as e:
                logger.error(f"Failed to sign transaction: {e}")
                raise ValueError(f"Failed to sign transaction: {str(e)}")
            
            # Send transaction
            try:
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                tx_hash_hex = self.w3.to_hex(tx_hash)
            except Exception as e:
                logger.error(f"Failed to broadcast transaction: {e}")
                error_msg = str(e).lower()
                
                # Handle specific errors
                if 'nonce too low' in error_msg:
                    raise ValueError(f"⏳ Transaction already pending. Please wait 10-15 seconds before sending another transaction.")
                elif 'replacement transaction underpriced' in error_msg:
                    raise ValueError(f"⛽ Previous transaction still pending. Wait for it to complete or increase gas price.")
                elif 'insufficient funds' in error_msg or 'balance' in error_msg:
                    raise ValueError(f"💰 Insufficient balance: {str(e)}")
                elif 'gas' in error_msg:
                    raise ValueError(f"⛽ Gas error: {str(e)}. Try with a higher gas price.")
                elif 'nonce' in error_msg:
                    raise ValueError(f"📋 Nonce error: {str(e)}. Wait a few seconds and try again.")
                else:
                    raise ValueError(f"❌ Transaction failed: {str(e)}")
            
            logger.info(f"✅ Transaction sent: {tx_hash_hex}")
            
            return {
                'tx_hash': tx_hash_hex,
                'from_address': from_address,
                'to_address': to_address,
                'amount': str(amount),
                'network': self.network,
                'explorer_url': f"{self.network_config['explorer']}/tx/{tx_hash_hex}",
                'status': 'pending'
            }
            
        except ValueError as e:
            # Re-raise ValueError with message intact
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending transaction: {e}")
            raise ValueError(f"Blockchain error: {str(e)}")
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Check transaction status
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Dict with status and confirmation info
        """
        try:
            # Get transaction receipt
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            if receipt:
                status = 'confirmed' if receipt['status'] == 1 else 'failed'
                return {
                    'status': status,
                    'block_number': receipt['blockNumber'],
                    'confirmations': self.w3.eth.block_number - receipt['blockNumber'],
                    'gas_used': receipt['gasUsed'],
                    'tx_hash': tx_hash
                }
            else:
                return {
                    'status': 'pending',
                    'tx_hash': tx_hash
                }
        except Exception as e:
            # Transaction not found yet (still pending)
            return {
                'status': 'pending',
                'tx_hash': tx_hash
            }
    
    def generate_new_wallet(self) -> Dict[str, str]:
        """
        Generate a new Ethereum wallet
        
        Returns:
            Dict with address and private_key
        """
        account = Account.create()
        return {
            'address': account.address,
            'private_key': account.key.hex()
        }
    
    def is_valid_address(self, address: str) -> bool:
        """
        Validate Ethereum address
        
        Args:
            address: Address to validate
            
        Returns:
            True if valid, False otherwise
        """
        return self.w3.is_address(address)


# Singleton instances for different networks
_blockchain_instances = {}


def get_blockchain_service(network: str = 'sepolia') -> BlockchainService:
    """
    Get or create blockchain service instance for a network
    
    Args:
        network: Network name
        
    Returns:
        BlockchainService instance
    """
    if network not in _blockchain_instances:
        _blockchain_instances[network] = BlockchainService(network)
    return _blockchain_instances[network]


if __name__ == "__main__":
    """Test blockchain service"""
    print("🧪 Testing Blockchain Service\n")
    
    # Test Sepolia connection
    try:
        bc = get_blockchain_service('sepolia')
        print(f"✅ Connected to {bc.network_config['name']}")
        
        # Test address validation
        test_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        is_valid = bc.is_valid_address(test_address)
        print(f"✅ Address validation: {is_valid}")
        
        # Only test balance if address is valid
        if is_valid:
            balance = bc.get_balance(test_address)
            print(f"✅ Balance check: {balance} ETH")
        else:
            print(f"⚠️  Skipping balance check (invalid address)")
        
        # Generate new wallet
        wallet = bc.generate_new_wallet()
        print(f"✅ Generated wallet: {wallet['address']}")
        print(f"   Private key: {wallet['private_key'][:20]}...") # Show first 20 chars only
        
        # Get balance of newly generated wallet
        new_balance = bc.get_balance(wallet['address'])
        print(f"✅ New wallet balance: {new_balance} ETH")
        
        print("\n✅ All tests passed!")
        print("\n📝 Next steps:")
        print("1. Get testnet ETH from https://sepoliafaucet.com")
        print(f"2. Send to your wallet: {wallet['address']}")
        print("3. Update .env with MASTER_WALLET_PRIVATE_KEY")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
