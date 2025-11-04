"""
Test Etherscan with real wallet address
"""
import logging
from etherscan_service import EtherscanService

logging.basicConfig(level=logging.INFO)

# Your actual wallet
WALLET_ADDRESS = "0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765"
API_KEY = "XEUGFHET25SI6JJ3GQ1C3VYZ41VH1AE7EY"

def main():
    print(f"🔍 Testing with wallet: {WALLET_ADDRESS}")
    print(f"🔑 API Key: {API_KEY}")
    print("=" * 70)
    
    service = EtherscanService(API_KEY, "sepolia")
    
    # Get all transactions
    print("\n📋 Fetching all transactions...")
    all_txs = service.get_normal_transactions(WALLET_ADDRESS)
    print(f"✅ Total transactions found: {len(all_txs)}")
    
    # Get incoming deposits
    print("\n💰 Filtering incoming deposits...")
    deposits = service.get_latest_incoming_deposits(WALLET_ADDRESS)
    print(f"✅ Incoming deposits found: {len(deposits)}")
    
    # Display deposits
    if deposits:
        print("\n📥 Deposit details:")
        for i, dep in enumerate(deposits, 1):
            print(f"\n  {i}. Amount: {dep['amount']} ETH")
            print(f"     From: {dep['from_address']}")
            print(f"     TX Hash: {dep['tx_hash']}")
            print(f"     Time: {dep['timestamp']}")
            print(f"     Block: {dep['block_number']}")
    else:
        print("\n⚠️ No deposits found!")

if __name__ == "__main__":
    main()
