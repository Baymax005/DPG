# DPG Technical Architecture

## System Overview

The Decentralized Payment Gateway (DPG) is built on a **microservices architecture** that ensures scalability, maintainability, and resilience. The system is designed to handle millions of concurrent users and process billions of dollars in transactions annually.

---

## Architecture Principles

1. **Microservices**: Independent, loosely coupled services
2. **Event-Driven**: Asynchronous communication via message queues
3. **API-First**: All services expose well-documented APIs
4. **Cloud-Native**: Designed for containerization and orchestration
5. **Security by Design**: Security integrated at every layer
6. **High Availability**: 99.9%+ uptime through redundancy
7. **Scalability**: Horizontal scaling for all services

---

## System Components

### 1. API Gateway Layer

**Technology**: Kong, AWS API Gateway

**Responsibilities**:
- Request routing and load balancing
- Authentication and authorization
- Rate limiting and throttling
- API versioning
- Request/response transformation
- Logging and monitoring

**Endpoints**:
- `/api/v1/auth/*` - Authentication services
- `/api/v1/wallets/*` - Wallet operations
- `/api/v1/trading/*` - Trading operations
- `/api/v1/payments/*` - Payment processing
- `/api/v1/cards/*` - Card management
- `/api/v1/merchant/*` - Business services

---

### 2. Core Services

#### 2.1 Authentication Service

**Technology**: Python, FastAPI, JWT, PostgreSQL

**Features**:
- User registration and login
- JWT token generation and validation
- OAuth 2.0 integration (Google, Apple)
- Two-factor authentication (TOTP, SMS)
- Session management
- Role-based access control (RBAC)
- Password hashing (bcrypt)
- Device fingerprinting

**Database Schema**:
```sql
users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  phone VARCHAR(20),
  kyc_status ENUM('pending', 'verified', 'rejected'),
  account_type ENUM('personal', 'business'),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

user_sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  token VARCHAR(500),
  device_info JSONB,
  ip_address VARCHAR(45),
  expires_at TIMESTAMP
)
```

**APIs**:
```
POST   /auth/register
POST   /auth/login
POST   /auth/logout
POST   /auth/refresh
POST   /auth/2fa/enable
POST   /auth/2fa/verify
GET    /auth/me
```

---

#### 2.2 Wallet Service

**Technology**: Python, FastAPI, PostgreSQL, SQLAlchemy

**Features**:
- Multi-currency fiat wallets (USD, EUR, GBP, etc.)
- Multi-cryptocurrency wallets (BTC, ETH, USDT, etc.)
- HD wallet generation (BIP32, BIP39, BIP44)
- Balance tracking and reconciliation
- Transaction history
- Wallet-to-wallet transfers
- Account statements

**Database Schema**:
```sql
wallets (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  currency_code VARCHAR(10),
  wallet_type ENUM('fiat', 'crypto'),
  balance DECIMAL(28, 18),
  available_balance DECIMAL(28, 18),
  address VARCHAR(255),
  created_at TIMESTAMP
)

transactions (
  id UUID PRIMARY KEY,
  wallet_id UUID REFERENCES wallets(id),
  type ENUM('deposit', 'withdrawal', 'transfer', 'conversion', 'fee'),
  amount DECIMAL(28, 18),
  currency VARCHAR(10),
  status ENUM('pending', 'completed', 'failed'),
  reference_id VARCHAR(100),
  metadata JSONB,
  created_at TIMESTAMP
)
```

**APIs**:
```
GET    /wallets
GET    /wallets/:id
GET    /wallets/:id/balance
GET    /wallets/:id/transactions
POST   /wallets/:id/transfer
```

---

#### 2.3 Trading Service

**Technology**: Python, FastAPI, Redis, WebSocket

**Features**:
- Order book management
- Matching engine (FIFO, Pro-rata)
- Order types (market, limit, stop-loss, take-profit)
- Trading pairs (50+ pairs)
- Real-time price feeds
- Trade execution
- Fee calculation
- Position tracking

**Order Matching Algorithm**:
```python
# High-performance matching engine
class MatchingEngine:
    def __init__(self):
        self.buy_orders = SortedList(key=lambda x: -x.price)  # Descending
        self.sell_orders = SortedList(key=lambda x: x.price)  # Ascending
    
    def match_order(self, order):
        if order.side == 'buy':
            while self.sell_orders and order.quantity > 0:
                if order.price >= self.sell_orders[0].price:
                    self.execute_trade(order, self.sell_orders[0])
                else:
                    break
        # Similar logic for sell orders
```

**Database Schema**:
```sql
trading_pairs (
  id UUID PRIMARY KEY,
  base_currency VARCHAR(10),
  quote_currency VARCHAR(10),
  min_order_size DECIMAL(28, 18),
  max_order_size DECIMAL(28, 18),
  maker_fee DECIMAL(5, 4),
  taker_fee DECIMAL(5, 4),
  is_active BOOLEAN
)

orders (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  trading_pair_id UUID REFERENCES trading_pairs(id),
  type ENUM('market', 'limit', 'stop_loss'),
  side ENUM('buy', 'sell'),
  price DECIMAL(28, 18),
  quantity DECIMAL(28, 18),
  filled_quantity DECIMAL(28, 18),
  status ENUM('pending', 'partial', 'filled', 'cancelled'),
  created_at TIMESTAMP
)

trades (
  id UUID PRIMARY KEY,
  buy_order_id UUID REFERENCES orders(id),
  sell_order_id UUID REFERENCES orders(id),
  trading_pair_id UUID REFERENCES trading_pairs(id),
  price DECIMAL(28, 18),
  quantity DECIMAL(28, 18),
  buyer_fee DECIMAL(28, 18),
  seller_fee DECIMAL(28, 18),
  executed_at TIMESTAMP
)
```

**APIs**:
```
GET    /trading/pairs
GET    /trading/orderbook/:pair
POST   /trading/orders
GET    /trading/orders/:id
DELETE /trading/orders/:id
GET    /trading/trades
WebSocket: wss://api.[domain]/trading/ws
```

---

#### 2.4 Payment Service

**Technology**: Python, FastAPI, Stripe, PostgreSQL

**Features**:
- Credit/debit card processing
- ACH/SEPA transfers
- Wire transfers (SWIFT)
- Payment method management
- Refund processing
- Chargeback handling
- Webhook management
- PCI DSS compliance

**Integration Partners**:
- **Stripe**: Primary card processor
- **Adyen**: International payments
- **Plaid**: Bank account linking
- **Synapse**: Banking infrastructure

**APIs**:
```
POST   /payments/deposit
POST   /payments/withdraw
GET    /payments/methods
POST   /payments/methods
DELETE /payments/methods/:id
POST   /payments/refund
```

---

#### 2.5 Blockchain Service

**Technology**: Node.js, Python, ethers.js, web3.js

**Features**:
- Blockchain node management (BTC, ETH, etc.)
- Wallet address generation
- Transaction broadcasting
- Transaction confirmation monitoring
- Gas fee estimation
- Smart contract interaction
- Token balance queries

**Supported Networks**:
- Bitcoin (BTC)
- Ethereum (ETH)
- Polygon (MATIC)
- Binance Smart Chain (BNB)
- ERC-20 tokens
- BEP-20 tokens

**Architecture**:
```
┌─────────────────┐
│ Blockchain API  │
└────────┬────────┘
         │
    ┌────┴────┐
    │  Router │
    └────┬────┘
         │
    ┌────┴──────────────────┐
    │                       │
┌───▼────┐           ┌─────▼─────┐
│ BTC    │           │ ETH/EVM   │
│ Service│           │ Service   │
└───┬────┘           └─────┬─────┘
    │                      │
┌───▼────┐           ┌─────▼─────┐
│Bitcoin │           │ Ethereum  │
│ Node   │           │ Node      │
└────────┘           └───────────┘
```

**APIs**:
```
POST   /blockchain/wallet/generate
GET    /blockchain/wallet/:address/balance
POST   /blockchain/transaction/send
GET    /blockchain/transaction/:txid
GET    /blockchain/gas/estimate
```

---

#### 2.6 Conversion Service

**Technology**: Node.js, Redis, PostgreSQL

**Features**:
- Real-time exchange rates
- Fiat-to-crypto conversion
- Crypto-to-fiat conversion
- Crypto-to-crypto swaps
- Fee calculation
- Slippage management
- Conversion limits
- Price oracles integration

**Price Aggregation**:
```javascript
class PriceAggregator {
  async getPrice(base, quote) {
    const prices = await Promise.all([
      this.coinGecko.getPrice(base, quote),
      this.coinMarketCap.getPrice(base, quote),
      this.binance.getPrice(base, quote)
    ]);
    
    // Calculate median to avoid outliers
    return this.calculateMedian(prices);
  }
}
```

**APIs**:
```
GET    /conversion/rates
POST   /conversion/convert
GET    /conversion/limits
PUT    /conversion/limits
```

---

#### 2.7 Card Service

**Technology**: Node.js, Marqeta/Galileo API

**Features**:
- Virtual card generation
- Physical card ordering
- Card activation
- PIN management
- Transaction authorization
- Spending limits
- Card freeze/unfreeze
- ATM withdrawal support

**Card Issuing Partners**:
- **Marqeta**: Primary card issuing platform
- **Galileo**: Alternative card processor
- **Visa**: Network partner
- **Mastercard**: Network partner

**APIs**:
```
POST   /cards/virtual/create
POST   /cards/physical/order
PUT    /cards/:id/activate
PUT    /cards/:id/freeze
GET    /cards/:id/transactions
PUT    /cards/:id/limits
```

---

#### 2.8 Merchant Service

**Technology**: Node.js, Express, PostgreSQL

**Features**:
- Business account management
- Payment gateway API
- Invoice generation
- Payment links
- Webhook management
- Settlement reporting
- Multi-user access control
- E-commerce plugins

**APIs**:
```
POST   /merchant/account/create
GET    /merchant/dashboard
POST   /merchant/invoices
POST   /merchant/payment-links
GET    /merchant/transactions
POST   /merchant/webhooks
```

---

### 3. Supporting Services

#### 3.1 Notification Service

**Technology**: Node.js, SendGrid, Twilio, FCM

**Features**:
- Email notifications
- SMS notifications
- Push notifications (mobile)
- In-app notifications
- Webhook delivery
- Template management

---

#### 3.2 Analytics Service

**Technology**: Python, Apache Spark, MongoDB

**Features**:
- User behavior tracking
- Transaction analytics
- Revenue reporting
- Fraud detection
- Performance monitoring

---

#### 3.3 Compliance Service

**Technology**: Node.js, Python, ML models

**Features**:
- KYC verification (Jumio, Onfido)
- AML transaction monitoring
- Sanctions screening
- Suspicious activity detection
- Regulatory reporting

---

## Data Flow Examples

### Example 1: User Converts USD to BTC

```
1. User initiates conversion: $1000 USD → BTC
2. API Gateway → Authentication (validate JWT)
3. API Gateway → Conversion Service
4. Conversion Service → Price Oracle (get BTC/USD rate)
5. Conversion Service → Wallet Service (check USD balance)
6. Conversion Service → Calculate: $1000 / $65,000 = 0.0153846 BTC
7. Conversion Service → Calculate fee (0.5%) = $5
8. Wallet Service → Debit $1005 from USD wallet
9. Blockchain Service → Credit 0.0153846 BTC to crypto wallet
10. Transaction logged → PostgreSQL
11. Event published → Kafka (for analytics, notifications)
12. Notification Service → Send confirmation email
13. Response returned to user
```

### Example 2: Spot Trading Order

```
1. User places limit buy order: 0.1 BTC @ $64,000
2. API Gateway → Authentication
3. API Gateway → Trading Service
4. Trading Service → Validate order params
5. Trading Service → Wallet Service (check quote currency balance)
6. Trading Service → Place order in order book
7. Trading Service → Matching Engine checks for matches
8. If match found:
   a. Execute trade
   b. Update wallet balances
   c. Record trade in database
   d. Publish trade event
   e. Notify both parties via WebSocket
9. If no match, order remains in book
```

---

## Security Architecture

### Multi-Layer Security

```
┌──────────────────────────────────────────┐
│  Layer 7: Application Security           │
│  - Input validation, Output encoding     │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│  Layer 6: API Security                   │
│  - JWT validation, Rate limiting         │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│  Layer 5: Network Security               │
│  - WAF, DDoS protection, TLS 1.3         │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│  Layer 4: Infrastructure Security        │
│  - VPC, Security groups, Encryption      │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│  Layer 3: Data Security                  │
│  - Encryption at rest, Key management    │
└──────────────────────────────────────────┘
```

### Key Management

- **Hot Wallets**: AWS KMS for encryption keys
- **Cold Wallets**: Hardware security modules (HSM)
- **API Keys**: Encrypted in database, rotated regularly
- **User Passwords**: bcrypt with salt (cost factor: 12)

---

## Scalability Strategy

### Horizontal Scaling

All services are stateless and can scale horizontally:
- **Load Balancers**: Distribute traffic across instances
- **Auto-Scaling**: Kubernetes HPA based on CPU/memory
- **Database Replication**: Read replicas for queries
- **Caching**: Redis for frequently accessed data

### Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time (p95) | <200ms |
| Trading Engine Latency | <10ms |
| Database Query Time (p95) | <50ms |
| Order Matching | 100K orders/sec |
| Concurrent Users | 1M+ |
| Transaction Throughput | 10K TPS |

---

## Disaster Recovery

### Backup Strategy

- **Database Backups**: Hourly incremental, daily full
- **Retention**: 30 days hot, 1 year cold
- **Geo-Replication**: Multi-region replication
- **Recovery Time Objective (RTO)**: <1 hour
- **Recovery Point Objective (RPO)**: <15 minutes

### Incident Response

1. **Detection**: Automated monitoring alerts
2. **Assessment**: Incident severity classification
3. **Containment**: Isolate affected services
4. **Recovery**: Restore from backups
5. **Post-Mortem**: Root cause analysis

---

## Monitoring & Observability

### Metrics Collection

- **Application Metrics**: Prometheus
- **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Traces**: Jaeger (distributed tracing)
- **Dashboards**: Grafana

### Key Metrics

- Request rate, error rate, duration (RED)
- CPU, memory, disk, network (USE)
- Transaction success/failure rates
- Wallet balance reconciliation
- Service dependencies health

---

## Technology Decisions

| Component | Technology | Reasoning |
|-----------|-----------|-----------|
| API Gateway | Kong | Feature-rich, scalable, plugin ecosystem |
| Backend | Node.js | Async I/O, npm ecosystem, JavaScript everywhere |
| Trading Engine | Python | Performance for numerical computation |
| Database | PostgreSQL | ACID compliance, complex queries, JSON support |
| Cache | Redis | Speed, pub/sub, data structures |
| Message Queue | Kafka | High throughput, durability, scalability |
| Container Orchestration | Kubernetes | Industry standard, auto-scaling, self-healing |
| Cloud Provider | AWS | Comprehensive services, reliability, global presence |

---

**Version**: 1.0  
**Last Updated**: October 25, 2025  
**Next Review**: Quarterly
