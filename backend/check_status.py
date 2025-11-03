"""Check transaction status"""
from database import SessionLocal
from models import Transaction

db = SessionLocal()
txs = db.query(Transaction).all()
print(f'\nTotal transactions: {len(txs)}\n')
for tx in txs:
    hash_str = tx.tx_hash[:20] + '...' if tx.tx_hash else 'No hash'
    print(f'  TX: {hash_str}')
    print(f'  Status: {tx.status.value}')
    print(f'  Amount: {tx.amount}')
    print(f'  Network: {tx.network}')
    print(f'  Date: {tx.created_at}')
    print()
db.close()
