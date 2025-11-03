#!/usr/bin/env python3
"""
Simple helper to fetch a transaction and its receipt from the configured Sepolia RPC.
Usage: python backend/check_tx.py <tx_hash>
"""
import sys
import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python check_tx.py <tx_hash>")
    sys.exit(1)

tx_hash = sys.argv[1]
rpc = os.getenv('SEPOLIA_RPC_URL', 'https://sepolia.infura.io/v3/YOUR_INFURA_KEY')

w3 = Web3(Web3.HTTPProvider(rpc))
print(f"RPC URL: {rpc}")
print(f"Connected: {w3.is_connected()}")

try:
    print('\nFetching transaction...')
    tx = w3.eth.get_transaction(tx_hash)
    print('Transaction:')
    print('  Hash:', tx.hash.hex())
    print('  From:', tx['from'])
    print('  To:', tx['to'])
    print('  Value (wei):', tx['value'])
    print('  Nonce:', tx['nonce'])
    print('  Gas:', tx['gas'])
    print('  GasPrice (wei):', tx.get('gasPrice'))
    print('  ChainId:', tx.get('chainId'))
except Exception as e:
    print('\nTransaction fetch error:', e)
    # continue to try receipt

try:
    print('\nFetching receipt...')
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    if receipt is None:
        print('Receipt: None (still pending or not yet mined)')
    else:
        print('Receipt:')
        print('  Status:', receipt.status)  # 1 = success, 0 = failed
        print('  BlockNumber:', receipt.blockNumber)
        print('  GasUsed:', receipt.gasUsed)
        print('  Logs count:', len(receipt.logs))
        print('  ContractAddress:', receipt.contractAddress)
        # confirmations
        try:
            current_block = w3.eth.block_number
            confirmations = current_block - receipt.blockNumber
            print('  Confirmations:', confirmations)
        except Exception:
            pass

        # Try to get revert reason if failed
        if receipt.status == 0:
            try:
                # call with same tx to get revert reason (simulate)
                print('\nTransaction failed (status=0). Attempting to get revert reason...')
                tx = w3.eth.get_transaction(tx_hash)
                # Build a call transaction copy
                call_tx = {
                    'to': tx['to'],
                    'from': tx['from'],
                    'data': tx['input'],
                    'value': tx['value']
                }
                reason = w3.eth.call(call_tx, tx.blockNumber)
                print('Revert reason (raw):', reason)
            except Exception as e:
                print('Could not fetch revert reason:', e)
except Exception as e:
    print('\nReceipt fetch error:', e)

# Also print current gas price & latest block
try:
    print('\nCurrent gas price (wei):', w3.eth.gas_price)
    print('Latest block:', w3.eth.block_number)
except Exception as e:
    print('Error fetching chain info:', e)

print('\nDone')
