# Contributing to DPG

Thank you for your interest in contributing to the Decentralized Payment Gateway (DPG)! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Requirements](#testing-requirements)
6. [Pull Request Process](#pull-request-process)
7. [Commit Message Guidelines](#commit-message-guidelines)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect:

- Respectful and professional communication
- Constructive feedback and criticism
- Focus on what is best for the project
- Empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory remarks
- Publishing others' private information
- Unprofessional conduct

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.10+ installed
- PostgreSQL 17+
- Git
- Code editor (VS Code recommended)
- Basic knowledge of FastAPI and SQLAlchemy

### Setting Up Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/DPG.git
cd DPG

# Add upstream remote
git remote add upstream https://github.com/Baymax005/DPG.git

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your actual credentials

# Setup database (PostgreSQL must be running)
# Create database: dpg_dev

# Start development server
cd backend
python main.py
```

---

## Development Workflow

### 1. Choose an Issue

- Browse [open issues](https://github.com/dpg-org/dpg/issues)
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to let others know you're working on it

### 2. Create a Branch

```bash
# Fetch latest changes
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### Branch Naming Convention:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding tests
- `chore/` - Maintenance tasks

### 3. Make Changes

- Write clean, readable code
- Follow coding standards (see below)
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add user authentication service"
```

### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

---

## Coding Standards

### Python

**Style Guide**: We follow PEP 8 with some project-specific conventions.

**Code Formatting**:
- Use **Black** for auto-formatting
- Maximum line length: 88 characters
- Use type hints where possible

**Best Practices**:
```python
# ✅ Good
from typing import Optional
from models import User

async def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Retrieve user by ID.
    
    Args:
        user_id: The user's database ID
        
    Returns:
        User object if found, None otherwise
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except Exception as e:
        logger.error(f'Failed to fetch user {user_id}: {e}')
        raise

# ❌ Bad
def get_user_by_id(user_id):
    user = db.query(User).filter(User.id == user_id).first()
    return user
```

**Naming Conventions**:
- **Variables/Functions**: snake_case (`user_name`, `total_amount`)
- **Classes**: PascalCase (`User`, `WalletService`)
- **Constants**: UPPER_SNAKE_CASE (`SECRET_KEY`, `MAX_AMOUNT`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`, `API_URL`)
- **Classes**: PascalCase (`UserService`, `PaymentController`)
- **Files**: kebab-case (`user-service.ts`, `payment-controller.ts`)
- **Interfaces**: PascalCase with "I" prefix optional (`User` or `IUser`)

### Python

**Style Guide**: PEP 8

**Example**:
```python
# ✅ Good
def calculate_trading_fee(amount: Decimal, fee_rate: Decimal) -> Decimal:
    """
    Calculate trading fee for a given amount.
    
    Args:
        amount: Trade amount
        fee_rate: Fee rate (e.g., 0.001 for 0.1%)
    
    Returns:
        Calculated fee amount
    """
    return amount * fee_rate

# ❌ Bad
def calculateTradingFee(amount, feeRate):
    return amount * feeRate
```

### Database

**Naming Conventions**:
- **Tables**: snake_case, plural (`users`, `transactions`)
- **Columns**: snake_case (`user_id`, `created_at`)
- **Indexes**: `idx_table_column` (`idx_users_email`)
- **Foreign Keys**: `fk_table1_table2` (`fk_wallets_users`)

### API Design

**RESTful Endpoints**:
```
GET    /api/v1/users          # List users
GET    /api/v1/users/:id      # Get user
POST   /api/v1/users          # Create user
PUT    /api/v1/users/:id      # Update user (full)
PATCH  /api/v1/users/:id      # Update user (partial)
DELETE /api/v1/users/:id      # Delete user
```

**Response Format**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com"
  },
  "message": "User created successfully",
  "timestamp": "2025-10-25T10:30:00Z"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Email is required",
    "details": {
      "field": "email"
    }
  },
  "timestamp": "2025-10-25T10:30:00Z"
}
```

---

## Testing Requirements

### Unit Tests

All new code must include unit tests.

**Coverage Requirements**: Minimum 80% code coverage

**Example (pytest)**:
```python
import pytest
from backend.wallet_service import WalletService
from backend.models import User

def test_create_wallet_with_valid_data(db_session):
    """Test wallet creation with valid data"""
    user = User(email='test@example.com', first_name='Test')
    db_session.add(user)
    db_session.commit()
    
    wallet = WalletService.create_wallet(
        user_id=user.id,
        currency_code='USD'
    )
    
    assert wallet is not None
    assert wallet.currency_code == 'USD'
    assert wallet.balance == 0
    
def test_duplicate_wallet_raises_error(db_session):
    """Test that duplicate wallet creation raises error"""
    user = User(email='test@example.com')
    db_session.add(user)
    db_session.commit()
    
    WalletService.create_wallet(user.id, 'USD')
    
    with pytest.raises(ValueError, match='Wallet already exists'):
        WalletService.create_wallet(user.id, 'USD')
```

### Integration Tests

Test interactions between services.

### E2E Tests

Test complete user flows.

**Running Tests**:
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=backend

# Run specific test file
python -m pytest tests/test_wallets.py

# Run in verbose mode
python -m pytest -v
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines (PEP 8)
- [ ] All tests pass (`python -m pytest`)
- [ ] Code coverage meets minimum (80%)
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts with main branch
- [ ] Self-review completed

### PR Template

When creating a PR, use this template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally

## Screenshots (if applicable)
Add screenshots here

## Related Issues
Closes #123
```

### Review Process

1. **Automated Checks**: CI/CD runs tests and linting
2. **Code Review**: At least 2 reviewers required
3. **Feedback**: Address all review comments
4. **Approval**: Once approved, maintainer will merge

### Merge Strategy

- **Squash and merge** for feature branches
- **Rebase and merge** for bug fixes
- **Merge commit** for release branches

---

## Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```bash
# Feature
feat(auth): add JWT token refresh mechanism

# Bug fix
fix(wallet): correct balance calculation for pending transactions

# Breaking change
feat(api)!: change response format for all endpoints

BREAKING CHANGE: API responses now use "data" field instead of direct object

# With scope and body
fix(trading): prevent order submission with insufficient balance

Added validation to check available balance before accepting order.
This prevents orders from being placed in the order book if the user
doesn't have sufficient funds.

Closes #456
```

---

## Documentation Standards

### Code Comments

```python
from decimal import Decimal
from typing import Dict

async def convert_currency(
    from_currency: str,
    to_currency: str,
    amount: Decimal
) -> Dict[str, Decimal]:
    """
    Calculate the conversion rate between two currencies.
    
    Args:
        from_currency: Source currency code (e.g., 'USD')
        to_currency: Target currency code (e.g., 'BTC')
        amount: Amount to convert
        
    Returns:
        Dict containing converted amount and fees
        
    Raises:
        ValueError: If currency is not supported
    """
    # Implementation
    pass
```

### API Documentation

All API endpoints are automatically documented using FastAPI's built-in Swagger UI.

### README Updates

Update README.md if your changes affect:
- Installation steps
- Configuration
- Usage examples
- Dependencies

---

## Security

### Reporting Vulnerabilities

**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email: security@dpg.com
2. Include detailed description
3. Provide steps to reproduce
4. Suggest a fix if possible

### Security Best Practices

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user inputs
- Use parameterized queries (prevent SQL injection)
- Implement rate limiting
- Follow OWASP guidelines

---

## Getting Help

- **Discord**: Join our [Discord server](https://discord.gg/dpg)
- **GitHub Discussions**: Ask questions in [Discussions](https://github.com/dpg-org/dpg/discussions)
- **Email**: dev@dpg.com

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Eligible for contributor rewards (coming soon)

---

Thank you for contributing to DPG! 🚀

**Last Updated**: October 25, 2025
