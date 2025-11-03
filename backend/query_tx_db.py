"""
Query DB for a transaction by tx_hash
Usage: python backend/query_tx_db.py <tx_hash>
"""
import sys
from dotenv import load_dotenv
import os
load_dotenv()

if len(sys.argv) < 2:
    print('Usage: python query_tx_db.py <tx_hash>')
    sys.exit(1)

tx_hash = sys.argv[1]

from database import SessionLocal
from models import Transaction

session = SessionLocal()
try:
    tx = session.query(Transaction).filter(Transaction.tx_hash == tx_hash).first()
    if not tx:
        print('No transaction record found with tx_hash =', tx_hash)
    else:
        print('Transaction found:')
        print('  id:', tx.id)
        print('  wallet_id:', tx.wallet_id)
        print('  amount:', tx.amount)
        print('  fee:', tx.fee)
        print('  status:', tx.status)
        print('  description:', tx.description)
        print('  created_at:', tx.created_at)
        print('  completed_at:', tx.completed_at)
finally:
    session.close()
