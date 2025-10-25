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

- Node.js 18+ installed
- Docker and Docker Compose
- PostgreSQL 14+
- Git
- Code editor (VS Code recommended)

### Setting Up Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/dpg.git
cd dpg

# Add upstream remote
git remote add upstream https://github.com/dpg-org/dpg.git

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start Docker services
docker-compose up -d

# Run migrations
npm run migrate

# Start development server
npm run dev
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

### TypeScript/JavaScript

**Style Guide**: We follow Airbnb JavaScript Style Guide with some modifications.

**ESLint Configuration**:
```javascript
{
  "extends": ["airbnb-typescript", "prettier"],
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error",
    "prefer-const": "error"
  }
}
```

**Best Practices**:
```typescript
// ✅ Good
async function getUserById(id: string): Promise<User | null> {
  try {
    const user = await userRepository.findById(id);
    return user;
  } catch (error) {
    logger.error('Failed to fetch user', { id, error });
    throw new DatabaseError('User retrieval failed');
  }
}

// ❌ Bad
async function getUserById(id) {
  const user = await userRepository.findById(id);
  return user;
}
```

**Naming Conventions**:
- **Variables**: camelCase (`userName`, `totalAmount`)
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

**Example (Jest)**:
```typescript
describe('UserService', () => {
  describe('createUser', () => {
    it('should create a new user with valid data', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'SecurePass123!'
      };
      
      const user = await userService.createUser(userData);
      
      expect(user).toBeDefined();
      expect(user.email).toBe(userData.email);
      expect(user.id).toBeDefined();
    });
    
    it('should throw error for duplicate email', async () => {
      const userData = { email: 'existing@example.com', password: 'pass' };
      
      await expect(userService.createUser(userData))
        .rejects
        .toThrow('Email already exists');
    });
  });
});
```

### Integration Tests

Test interactions between services.

### E2E Tests

Test complete user flows.

**Running Tests**:
```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- user-service.test.ts

# Run in watch mode
npm run test:watch
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass (`npm test`)
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

```typescript
/**
 * Calculates the conversion rate between two currencies.
 * 
 * @param fromCurrency - Source currency code (e.g., 'USD')
 * @param toCurrency - Target currency code (e.g., 'BTC')
 * @param amount - Amount to convert
 * @returns Converted amount with fee included
 * @throws {InvalidCurrencyError} If currency is not supported
 */
async function convertCurrency(
  fromCurrency: string,
  toCurrency: string,
  amount: Decimal
): Promise<ConversionResult> {
  // Implementation
}
```

### API Documentation

All API endpoints must be documented using OpenAPI/Swagger.

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
