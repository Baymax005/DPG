"""
Proof of Reserves Routes
Public endpoints for transparency and auditing
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from decimal import Decimal
from datetime import datetime

from database import get_db
from proof_of_reserves import ProofOfReservesService

router = APIRouter(prefix="/api/v1/reserves", tags=["Proof of Reserves"])


@router.get("/report", response_model=Dict)
async def get_proof_of_reserves_report(
    include_onchain: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get complete Proof of Reserves report
    
    **Public endpoint** - No authentication required for transparency
    
    Query Parameters:
    - include_onchain: Whether to include on-chain verification (default: True)
    
    Returns:
    - Total reserves by currency
    - Total liabilities
    - Solvency ratios
    - Merkle tree roots for verification
    - On-chain balance verification (if enabled)
    - User and wallet counts
    
    This endpoint demonstrates full transparency by showing:
    1. How much crypto/fiat the platform holds (reserves)
    2. How much is owed to users (liabilities)
    3. Solvency ratio (should be >= 100% for fully reserved)
    4. Merkle tree root for cryptographic verification
    5. On-chain verification that reserve wallets match database
    """
    try:
        report = ProofOfReservesService.get_proof_of_reserves_report(
            db, 
            include_onchain=include_onchain
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating proof of reserves: {str(e)}"
        )


@router.get("/merkle/{currency}")
async def get_merkle_tree(currency: str, db: Session = Depends(get_db)):
    """
    Get Merkle tree for a specific currency
    
    **Public endpoint** - Anyone can verify the Merkle root
    
    Args:
        currency: Currency code (ETH, BTC, USD, etc.)
    
    Returns:
        Merkle tree root and metadata for verification
    """
    try:
        currency = currency.upper()
        merkle_data = ProofOfReservesService.generate_merkle_tree(db, currency)
        
        if merkle_data['merkle_root'] is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No balances found for currency: {currency}"
            )
        
        return merkle_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating Merkle tree: {str(e)}"
        )


@router.get("/solvency")
async def get_solvency_status(db: Session = Depends(get_db)):
    """
    Get solvency status for all currencies
    
    **Public endpoint** - Shows platform is fully reserved
    
    Returns:
        Solvency ratios for each currency
        - 100% = Fully reserved (good!)
        - > 100% = Over-reserved (very good!)
        - < 100% = Under-reserved (bad! - fractional reserve)
    """
    try:
        report = ProofOfReservesService.get_proof_of_reserves_report(db, include_onchain=False)
        return {
            'solvency': report['solvency'],
            'timestamp': report['timestamp'],
            'fully_reserved': all(
                s['fully_reserved'] 
                for s in report['solvency'].values()
            ),
            'note': 'A solvency ratio of 100% or more indicates the platform is fully reserved'
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating solvency: {str(e)}"
        )


@router.get("/onchain")
async def get_onchain_verification(db: Session = Depends(get_db)):
    """
    Get on-chain balance verification
    
    **Public endpoint** - Verify reserves directly from blockchain
    
    Returns:
        Comparison of database balances vs on-chain balances
        - Shows reserve wallet addresses
        - Compares database totals with actual blockchain balances
        - Provides match percentage and verification status
    
    This is the ultimate proof - anyone can verify these addresses
    on Etherscan/Polygonscan and confirm the platform holds what it claims.
    """
    try:
        from proof_of_reserves import OnChainReserveTracker
        
        tracker = OnChainReserveTracker()
        onchain_reserves = tracker.verify_all_reserves()
        
        # Get database reserves for comparison
        db_reserves = ProofOfReservesService.calculate_total_reserves(db)
        
        comparison = {}
        for currency in onchain_reserves.keys():
            onchain_total = Decimal(onchain_reserves[currency]['total'])
            db_total = db_reserves.get(currency, {}).get('total', Decimal('0'))
            
            difference = onchain_total - db_total
            match_percent = (db_total / onchain_total * 100) if onchain_total > 0 else Decimal('0')
            
            comparison[currency] = {
                'database_balance': str(db_total),
                'onchain_balance': str(onchain_total),
                'difference': str(difference),
                'match_percent': str(match_percent.quantize(Decimal('0.01'))),
                'status': 'VERIFIED' if abs(difference) < Decimal('0.001') else 'MISMATCH',
                'reserve_wallets': onchain_reserves[currency]['wallets'],
                'explorer_links': [
                    f"https://sepolia.etherscan.io/address/{addr}" 
                    for addr in onchain_reserves[currency]['wallets']
                ]
            }
        
        return {
            'network': 'Sepolia Testnet',
            'verified_at': datetime.utcnow().isoformat(),
            'comparison': comparison,
            'note': 'Anyone can verify these addresses on Etherscan to confirm reserves'
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying on-chain reserves: {str(e)}"
        )
