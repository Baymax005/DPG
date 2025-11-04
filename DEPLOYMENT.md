# 🚀 Production Deployment Guide

## Overview
This guide covers deploying the DPG (Digital Payment Gateway) platform to production with security best practices, monitoring, and maintenance procedures.

---

## 📋 Pre-Deployment Checklist

### Security Audit
- [ ] Code review completed
- [ ] Security vulnerabilities scanned
- [ ] Dependencies updated to latest stable versions
- [ ] Penetration testing performed
- [ ] SQL injection tests passed
- [ ] XSS protection verified
- [ ] CSRF tokens implemented

### Infrastructure
- [ ] Domain name registered
- [ ] SSL/TLS certificates obtained
- [ ] Cloud provider account setup
- [ ] Database server provisioned
- [ ] Backup storage configured
- [ ] CDN configured (optional)

### Environment
- [ ] Production environment variables configured
- [ ] Secrets management system setup
- [ ] Monitoring tools installed
- [ ] Logging infrastructure ready
- [ ] Error tracking enabled

---

## 🏗️ Infrastructure Setup

### Recommended Stack

#### Cloud Providers (Choose One)
- **AWS** (Recommended for enterprise)
  - EC2 for application server
  - RDS for PostgreSQL
  - S3 for backups
  - CloudWatch for monitoring
  
- **DigitalOcean** (Recommended for startups)
  - Droplets for servers
  - Managed PostgreSQL
  - Spaces for backups
  - Built-in monitoring

- **Google Cloud Platform**
  - Compute Engine
  - Cloud SQL
  - Cloud Storage

- **Azure**
  - Virtual Machines
  - Azure Database for PostgreSQL
  - Blob Storage

### Server Requirements

#### Application Server
- **OS:** Ubuntu 22.04 LTS or later
- **CPU:** 2+ cores
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 50GB SSD minimum
- **Python:** 3.13+
- **Network:** Static IP address

#### Database Server
- **PostgreSQL:** 14+ (17 recommended)
- **CPU:** 2+ cores
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 100GB SSD minimum (with room to grow)
- **Backup:** Daily automated backups with 30-day retention

---

## 🔐 Security Configuration

### 1. Wallet Encryption Key (CRITICAL)

**DO NOT use development encryption keys in production!**

#### Using Cloud KMS (Recommended)

**AWS KMS:**
```bash
# Create KMS key
aws kms create-key --description "DPG Wallet Encryption Key"

# Get key ID
KEY_ID="arn:aws:kms:region:account:key/key-id"

# Store in environment
echo "WALLET_ENCRYPTION_KEY_ID=$KEY_ID" >> /etc/dpg/.env
```

**Google Cloud KMS:**
```bash
# Create keyring
gcloud kms keyrings create dpg-keyring --location global

# Create encryption key
gcloud kms keys create wallet-encryption-key \
  --location global \
  --keyring dpg-keyring \
  --purpose encryption

# Get key resource name
KEY_NAME="projects/PROJECT_ID/locations/global/keyRings/dpg-keyring/cryptoKeys/wallet-encryption-key"
```

**Azure Key Vault:**
```bash
# Create key vault
az keyvault create --name dpg-keyvault --resource-group dpg-rg

# Create encryption key
az keyvault key create --vault-name dpg-keyvault --name wallet-encryption-key

# Get key URI
KEY_URI="https://dpg-keyvault.vault.azure.net/keys/wallet-encryption-key"
```

#### Manual Key Generation (Alternative)
```python
# Generate secure encryption key
from cryptography.fernet import Fernet
import secrets

# Generate Fernet key
fernet_key = Fernet.generate_key()
print(f"WALLET_ENCRYPTION_KEY={fernet_key.decode()}")

# Generate JWT secret (32+ characters)
jwt_secret = secrets.token_urlsafe(64)
print(f"SECRET_KEY={jwt_secret}")
```

**Store keys in secure vault or environment variables - NEVER commit to git!**

### 2. Database Security

#### PostgreSQL Configuration
```sql
-- Create production database and user
CREATE USER dpg_prod WITH PASSWORD 'STRONG_PASSWORD_HERE';
CREATE DATABASE dpg_production OWNER dpg_prod;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE dpg_production TO dpg_prod;

-- Enable SSL connections
ALTER SYSTEM SET ssl = on;
```

#### Firewall Rules
```bash
# Allow only application server to connect
sudo ufw allow from <APP_SERVER_IP> to any port 5432
sudo ufw enable
```

#### Connection String
```bash
# Production database URL with SSL
DATABASE_URL=postgresql://dpg_prod:PASSWORD@db-server:5432/dpg_production?sslmode=require
```

### 3. Environment Variables

Create `/etc/dpg/.env.production`:
```bash
# ============================================
# PRODUCTION ENVIRONMENT CONFIGURATION
# ============================================

# Application
NODE_ENV=production
DEBUG=False
ENVIRONMENT=production

# Server
PORT=8000
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://dpg_prod:PASSWORD@localhost:5432/dpg_production?sslmode=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Security - JWT
SECRET_KEY=<YOUR_64_CHARACTER_SECRET_KEY>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Security - Wallet Encryption
WALLET_ENCRYPTION_KEY=<YOUR_FERNET_KEY>
# Or use KMS:
# WALLET_ENCRYPTION_KEY_ID=<AWS_KMS_KEY_ID>

# Blockchain - Mainnet (REPLACE TESTNET URLS!)
SEPOLIA_RPC_URL=https://mainnet.infura.io/v3/<INFURA_PROJECT_ID>
ETH_RPC_URL=https://mainnet.infura.io/v3/<INFURA_PROJECT_ID>
POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/<INFURA_PROJECT_ID>

INFURA_API_KEY=<YOUR_MAINNET_INFURA_KEY>
ETHERSCAN_API_KEY=<YOUR_MAINNET_ETHERSCAN_KEY>
POLYGONSCAN_API_KEY=<YOUR_MAINNET_POLYGONSCAN_KEY>

# Reserve Wallets (Production addresses)
ETH_RESERVE_WALLETS=<YOUR_MAINNET_ETH_WALLET>
USDT_RESERVE_WALLETS=<YOUR_MAINNET_USDT_WALLET>
USDC_RESERVE_WALLETS=<YOUR_MAINNET_USDC_WALLET>

# Email (SendGrid)
SENDGRID_API_KEY=<YOUR_SENDGRID_API_KEY>
EMAIL_FROM=noreply@yourdomain.com

# Monitoring
SENTRY_DSN=<YOUR_SENTRY_DSN>
LOG_LEVEL=INFO

# CORS (Your production domain)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
```

---

## 🌐 Domain & SSL Setup

### 1. Domain Configuration

**DNS Records:**
```
A     @           <SERVER_IP>
A     www         <SERVER_IP>
CNAME api         yourdomain.com
```

### 2. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

### 3. Nginx Configuration

Create `/etc/nginx/sites-available/dpg`:
```nginx
# Frontend
server {
    listen 80;
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Redirect HTTP to HTTPS
    if ($scheme != "https") {
        return 301 https://$host$request_uri;
    }

    location / {
        root /var/www/dpg/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}

# Backend API
server {
    listen 80;
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Redirect HTTP to HTTPS
    if ($scheme != "https") {
        return 301 https://$host$request_uri;
    }

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
}
```

Enable configuration:
```bash
sudo ln -s /etc/nginx/sites-available/dpg /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📦 Application Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.13 python3.13-venv python3-pip postgresql-client nginx git

# Create application user
sudo useradd -m -s /bin/bash dpg
sudo su - dpg

# Clone repository
cd /home/dpg
git clone https://github.com/Baymax005/DPG.git
cd DPG

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 2. Database Migration

```bash
# Copy production env file
sudo cp /etc/dpg/.env.production /home/dpg/DPG/.env
sudo chown dpg:dpg /home/dpg/DPG/.env
sudo chmod 600 /home/dpg/DPG/.env

# Run database migrations
cd /home/dpg/DPG/backend
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 3. Systemd Service

Create `/etc/systemd/system/dpg.service`:
```ini
[Unit]
Description=DPG Backend Service
After=network.target postgresql.service

[Service]
Type=simple
User=dpg
Group=dpg
WorkingDirectory=/home/dpg/DPG/backend
Environment="PATH=/home/dpg/DPG/venv/bin"
EnvironmentFile=/etc/dpg/.env.production
ExecStart=/home/dpg/DPG/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Restart policy
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/dpg/DPG/logs

# Logging
StandardOutput=append:/var/log/dpg/access.log
StandardError=append:/var/log/dpg/error.log

[Install]
WantedBy=multi-user.target
```

Create log directories:
```bash
sudo mkdir -p /var/log/dpg
sudo chown dpg:dpg /var/log/dpg
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable dpg
sudo systemctl start dpg
sudo systemctl status dpg
```

### 4. Frontend Deployment

```bash
# Copy frontend files
sudo mkdir -p /var/www/dpg
sudo cp -r /home/dpg/DPG/frontend/* /var/www/dpg/
sudo chown -R www-data:www-data /var/www/dpg

# Update API URL in frontend
sudo sed -i 's|http://localhost:8000|https://api.yourdomain.com|g' /var/www/dpg/app.js
```

---

## 💾 Backup Strategy

### 1. Database Backups

#### Automated Daily Backups
Create `/home/dpg/scripts/backup_database.sh`:
```bash
#!/bin/bash

BACKUP_DIR="/home/dpg/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="dpg_production_${DATE}.sql.gz"

mkdir -p $BACKUP_DIR

# Dump database
pg_dump postgresql://dpg_prod:PASSWORD@localhost:5432/dpg_production | gzip > "$BACKUP_DIR/$FILENAME"

# Upload to S3 (optional but recommended)
aws s3 cp "$BACKUP_DIR/$FILENAME" s3://dpg-backups/database/

# Keep only last 30 days locally
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $FILENAME"
```

Make executable and schedule:
```bash
chmod +x /home/dpg/scripts/backup_database.sh

# Add to crontab
crontab -e
# Add line:
0 2 * * * /home/dpg/scripts/backup_database.sh >> /var/log/dpg/backup.log 2>&1
```

### 2. Application Backups

```bash
# Backup configuration and code
tar -czf dpg_app_backup_$(date +%Y%m%d).tar.gz /home/dpg/DPG /etc/dpg

# Upload to S3
aws s3 cp dpg_app_backup_$(date +%Y%m%d).tar.gz s3://dpg-backups/application/
```

### 3. Backup Restoration

```bash
# Restore database
gunzip -c backup_file.sql.gz | psql postgresql://dpg_prod:PASSWORD@localhost:5432/dpg_production

# Restore application
tar -xzf dpg_app_backup_YYYYMMDD.tar.gz -C /
sudo systemctl restart dpg
```

---

## 📊 Monitoring & Logging

### 1. Application Monitoring (Sentry)

```bash
# Install Sentry SDK (already in requirements.txt)
pip install sentry-sdk

# Add to backend/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment="production"
)
```

### 2. Server Monitoring

#### Install monitoring tools:
```bash
# Install node_exporter for Prometheus
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.0/node_exporter-1.6.0.linux-amd64.tar.gz
tar xvfz node_exporter-*.tar.gz
sudo mv node_exporter-*/node_exporter /usr/local/bin/
sudo useradd -rs /bin/false node_exporter

# Create systemd service
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

### 3. Log Management

#### Centralized logging:
```bash
# Install Logrotate configuration
sudo tee /etc/logrotate.d/dpg > /dev/null <<EOF
/var/log/dpg/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 dpg dpg
    sharedscripts
    postrotate
        systemctl reload dpg > /dev/null 2>&1 || true
    endscript
}
EOF
```

### 4. Health Checks

Create `/home/dpg/scripts/health_check.sh`:
```bash
#!/bin/bash

# Check API health
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://api.yourdomain.com/docs)

if [ "$API_STATUS" != "200" ]; then
    echo "API DOWN - Status: $API_STATUS"
    # Send alert (email, Slack, etc.)
    curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"🚨 DPG API is DOWN!"}' \
      YOUR_SLACK_WEBHOOK_URL
else
    echo "API OK - Status: $API_STATUS"
fi

# Check database
DB_STATUS=$(PGPASSWORD=PASSWORD psql -h localhost -U dpg_prod -d dpg_production -c "SELECT 1" -q)

if [ $? -ne 0 ]; then
    echo "DATABASE DOWN"
    # Send alert
fi
```

Schedule health checks:
```bash
*/5 * * * * /home/dpg/scripts/health_check.sh >> /var/log/dpg/health.log 2>&1
```

---

## 🔄 Continuous Deployment

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: dpg
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /home/dpg/DPG
            git pull origin main
            source venv/bin/activate
            pip install -r backend/requirements.txt
            sudo systemctl restart dpg
            echo "Deployment completed!"
```

---

## 🛡️ Security Hardening

### 1. Firewall Configuration

```bash
# Allow SSH (change default port for security)
sudo ufw allow 2222/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### 2. SSH Hardening

Edit `/etc/ssh/sshd_config`:
```
Port 2222
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

```bash
sudo systemctl restart sshd
```

### 3. Fail2Ban

```bash
# Install
sudo apt install fail2ban

# Configure
sudo tee /etc/fail2ban/jail.local > /dev/null <<EOF
[sshd]
enabled = true
port = 2222
maxretry = 3

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📈 Performance Optimization

### 1. Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_wallets_user_id ON wallets(user_id);
CREATE INDEX idx_wallets_currency ON wallets(currency_code);
CREATE INDEX idx_transactions_wallet_id ON transactions(wallet_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);

-- Vacuum and analyze
VACUUM ANALYZE;
```

### 2. Application Caching

Consider implementing Redis for caching:
```bash
sudo apt install redis-server
pip install redis
```

### 3. CDN Setup (Optional)

Use Cloudflare or AWS CloudFront for frontend assets.

---

## 🚨 Incident Response

### 1. Service Down

```bash
# Check service status
sudo systemctl status dpg

# View recent logs
sudo journalctl -u dpg -n 100 --no-pager

# Restart service
sudo systemctl restart dpg
```

### 2. High Load

```bash
# Check system resources
htop
df -h

# Check connections
ss -tuln | grep 8000

# Scale workers
# Edit /etc/systemd/system/dpg.service
# Change: --workers 4 to --workers 8
sudo systemctl daemon-reload
sudo systemctl restart dpg
```

### 3. Database Issues

```bash
# Check connections
psql -U dpg_prod -d dpg_production -c "SELECT count(*) FROM pg_stat_activity;"

# Kill stuck queries
psql -U dpg_prod -d dpg_production -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='dpg_production' AND state='idle in transaction';"
```

---

## ✅ Post-Deployment Verification

### 1. Smoke Tests

```bash
# Test API
curl https://api.yourdomain.com/docs

# Test authentication
curl -X POST https://api.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# Test proof of reserves
curl https://api.yourdomain.com/api/v1/reserves/report
```

### 2. Frontend Tests

- [ ] Login works
- [ ] Wallet creation works
- [ ] Transactions display correctly
- [ ] Proof of reserves loads
- [ ] Transaction receipts generate
- [ ] All links work (no 404s)

### 3. Security Tests

- [ ] HTTPS enforced (HTTP redirects)
- [ ] SSL certificate valid
- [ ] CORS configured correctly
- [ ] Rate limiting working
- [ ] Authentication required for protected routes

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

**Daily:**
- Monitor error logs
- Check backup completion
- Review transaction processing

**Weekly:**
- Update dependencies
- Review security advisories
- Check disk space

**Monthly:**
- Review and rotate logs
- Update SSL certificates (if manual)
- Security audit
- Performance review

### Contact Information

**Emergency Contacts:**
- Developer: Muhammad Ali (@baymax005)
- Email: support@dpg.example.com
- Status Page: status.yourdomain.com

---

## 📚 Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Production Checklist](https://www.postgresql.org/docs/current/admin.html)
- [Nginx Security](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [AWS Best Practices](https://aws.amazon.com/architecture/well-architected/)

---

**Last Updated:** November 5, 2025  
**Version:** 1.0  
**Author:** Muhammad Ali (@baymax005)

**🎉 Congratulations on deploying DPG to production!**
