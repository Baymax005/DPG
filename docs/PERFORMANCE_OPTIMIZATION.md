# Performance Optimization Plan

## Current Performance Issues

### Test Results:
- **10 deposits**: 20.62 seconds (~2 sec/transaction)
- **10 withdrawals**: 20.66 seconds (~2 sec/transaction)

### Projected Impact at Scale:
- **1,000 concurrent users**: ~33 minutes
- **10,000 concurrent users**: ~5.5 hours
- **1,000,000 concurrent users**: ~23 days
- **This is UNACCEPTABLE for production** ❌

## Root Causes

1. **Individual Database Commits**
   - Each transaction commits separately
   - No batch processing
   - Database lock contention

2. **Missing Database Indexes**
   - No indexes on `wallet_id`, `user_id`, `created_at`
   - Slow lookups and joins

3. **Synchronous Processing**
   - All transactions block the API
   - No async queue for non-critical operations

4. **No Connection Pooling**
   - Each request creates new connection
   - No reuse of database connections

5. **No Caching**
   - Balance recalculated every time
   - User data fetched on every request

## Optimization Strategy

### Phase 1: Quick Wins (1-2 days)

#### 1.1 Add Database Indexes
```sql
-- User indexes
CREATE INDEX idx_users_email ON users(email);

-- Wallet indexes
CREATE INDEX idx_wallets_user_id ON wallets(user_id);
CREATE INDEX idx_wallets_currency ON wallets(currency_code);

-- Transaction indexes
CREATE INDEX idx_transactions_wallet_id ON transactions(wallet_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_type ON transactions(type);

-- Composite indexes for common queries
CREATE INDEX idx_wallets_user_currency ON wallets(user_id, currency_code);
CREATE INDEX idx_transactions_wallet_created ON transactions(wallet_id, created_at DESC);
```

**Expected Improvement**: 50-70% faster queries

#### 1.2 Database Connection Pooling
```python
# database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Keep 20 connections alive
    max_overflow=10,     # Allow 10 extra connections
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600    # Recycle connections every hour
)
```

**Expected Improvement**: 30-40% faster response times

#### 1.3 Batch Processing for Multiple Transactions
```python
@staticmethod
def batch_deposit(db: Session, deposits: List[dict]) -> List[Transaction]:
    """Process multiple deposits in one transaction"""
    transactions = []
    
    for deposit_data in deposits:
        wallet = db.query(Wallet).filter(Wallet.id == deposit_data['wallet_id']).first()
        wallet.balance += deposit_data['amount']
        
        transaction = Transaction(...)
        transactions.append(transaction)
        db.add(transaction)
    
    db.commit()  # Single commit for all
    return transactions
```

**Expected Improvement**: 80-90% faster for bulk operations

### Phase 2: Medium-Term (1 week)

#### 2.1 Redis Caching
```python
# Cache user balance
cache.set(f"balance:{wallet_id}", balance, ex=60)  # 60 sec TTL

# Cache user data
cache.set(f"user:{user_id}", user_data, ex=300)  # 5 min TTL
```

**Expected Improvement**: 90% reduction in DB reads

#### 2.2 Async Task Queue (Celery)
```python
@celery.task
def process_withdrawal_async(wallet_id, amount):
    """Process withdrawal in background"""
    # Blockchain interaction happens here
    # Email notifications
    # Audit logging
```

**Expected Improvement**: API responds in <100ms, processing happens in background

#### 2.3 Read Replicas
- **Master**: Handle writes (deposits, withdrawals, transfers)
- **Replicas**: Handle reads (balance checks, transaction history)

**Expected Improvement**: 10x read capacity

### Phase 3: Production Scale (2-4 weeks)

#### 3.1 Horizontal Scaling
- Multiple FastAPI instances behind load balancer
- Auto-scaling based on traffic

#### 3.2 Database Partitioning
- Partition transactions by date (monthly tables)
- Shard wallets by user_id hash

#### 3.3 Event-Driven Architecture
```
User Request → API → Message Queue → Workers → Database
                ↓
            Immediate Response (202 Accepted)
```

#### 3.4 CDN for Static Assets
- Frontend served from CDN
- API only handles dynamic requests

## Performance Targets

### After Phase 1 (Quick Wins):
- ✅ **10 transactions**: <2 seconds (10x improvement)
- ✅ **100 transactions**: <5 seconds
- ✅ **1,000 concurrent users**: <10 seconds

### After Phase 2 (Medium-Term):
- ✅ **10 transactions**: <500ms (40x improvement)
- ✅ **1,000 transactions**: <5 seconds
- ✅ **10,000 concurrent users**: <30 seconds

### After Phase 3 (Production Scale):
- ✅ **10 transactions**: <100ms (200x improvement)
- ✅ **100,000 transactions/sec**: Sustained throughput
- ✅ **1M concurrent users**: No degradation

## Implementation Priority

### IMMEDIATE (This Week):
1. ✅ Add database indexes (30 min)
2. ✅ Enable connection pooling (15 min)
3. ✅ Optimize transaction queries (1 hour)

### NEXT WEEK:
4. Redis caching setup
5. Background task queue
6. Database read replicas

### BEFORE MAINNET:
7. Horizontal scaling
8. Load balancer
9. Monitoring & alerting

## Monitoring

### Metrics to Track:
- **Avg response time**: <200ms target
- **P95 response time**: <500ms target
- **P99 response time**: <1000ms target
- **Throughput**: Transactions per second
- **Error rate**: <0.1% target
- **Database connection pool usage**
- **Cache hit rate**: >90% target

### Tools:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **DataDog/New Relic**: APM
- **Sentry**: Error tracking

## Cost Considerations

### Phase 1: FREE
- Just code changes

### Phase 2: ~$50-100/month
- Redis (DigitalOcean: $15/month)
- Celery workers (extra droplet: $24/month)

### Phase 3: ~$500-1000/month
- Load balancer: $20/month
- Multiple API servers: 3 x $24 = $72/month
- Database replicas: 2 x $60 = $120/month
- Redis cluster: $60/month
- Monitoring: $50/month

## Next Steps

1. **Immediate**: Implement Phase 1 optimizations
2. **Test**: Re-run stress tests, target <2 sec for 10 transactions
3. **Benchmark**: Test with 100, 1000, 10000 transactions
4. **Plan Phase 2**: Schedule Redis + Celery implementation
5. **Monitor**: Set up basic monitoring before testnet launch

---

**Status**: Planning
**Priority**: CRITICAL
**Deadline**: Phase 1 by Oct 28, Phase 2 by Nov 3 (before testnet launch)
