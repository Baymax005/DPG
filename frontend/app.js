// DPG Frontend - JavaScript
const API_URL = 'http://localhost:9000';
let authToken = localStorage.getItem('dpg_token');
let currentUser = null;
let wallets = [];

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    if (authToken) {
        loadDashboard();
    } else {
        showLoginPage();
    }
});

// Toggle password visibility
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(inputId + '-icon');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Show/Hide Pages
function showLoginPage() {
    document.getElementById('loginPage').classList.remove('hidden');
    document.getElementById('dashboardPage').classList.add('hidden');
    document.getElementById('navButtons').classList.add('hidden');
}

function showDashboard() {
    document.getElementById('loginPage').classList.add('hidden');
    document.getElementById('dashboardPage').classList.remove('hidden');
    document.getElementById('navButtons').classList.remove('hidden');
}

// Toggle between Login and Register tabs
function showLoginTab() {
    document.getElementById('loginForm').classList.remove('hidden');
    document.getElementById('registerForm').classList.add('hidden');
    document.getElementById('loginTabBtn').classList.add('bg-white', 'text-purple-600', 'shadow');
    document.getElementById('loginTabBtn').classList.remove('text-gray-600');
    document.getElementById('registerTabBtn').classList.remove('bg-white', 'text-purple-600', 'shadow');
    document.getElementById('registerTabBtn').classList.add('text-gray-600');
}

function showRegisterTab() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('registerForm').classList.remove('hidden');
    document.getElementById('registerTabBtn').classList.add('bg-white', 'text-purple-600', 'shadow');
    document.getElementById('registerTabBtn').classList.remove('text-gray-600');
    document.getElementById('loginTabBtn').classList.remove('bg-white', 'text-purple-600', 'shadow');
    document.getElementById('loginTabBtn').classList.add('text-gray-600');
}

// Register
async function register() {
    const email = document.getElementById('registerEmail').value.trim();
    const password = document.getElementById('registerPassword').value;
    const firstName = document.getElementById('registerFirstName').value.trim();
    const lastName = document.getElementById('registerLastName').value.trim();
    
    // Validation
    if (!email) {
        showError('registerError', 'Please enter your email');
        return;
    }
    if (!password) {
        showError('registerError', 'Please enter a password');
        return;
    }
    if (!firstName) {
        showError('registerError', 'Please enter your first name');
        return;
    }
    if (!lastName) {
        showError('registerError', 'Please enter your last name');
        return;
    }
    
    // Hide previous messages
    document.getElementById('registerError').classList.add('hidden');
    document.getElementById('registerSuccess').classList.add('hidden');
    
    try {
        const response = await fetch(`${API_URL}/api/v1/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email,
                password,
                first_name: firstName,
                last_name: lastName
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Show success message
            const successDiv = document.getElementById('registerSuccess');
            successDiv.textContent = 'Account created successfully! Please login.';
            successDiv.classList.remove('hidden');
            
            // Clear form
            document.getElementById('registerEmail').value = '';
            document.getElementById('registerPassword').value = '';
            document.getElementById('registerFirstName').value = '';
            document.getElementById('registerLastName').value = '';
            
            // Switch to login tab after 2 seconds
            setTimeout(() => {
                showLoginTab();
                document.getElementById('loginEmail').value = email;
            }, 2000);
        } else {
            // Handle validation errors (array format) or simple string errors
            let errorMsg = 'Registration failed';
            if (Array.isArray(data.detail)) {
                // Pydantic validation errors - extract readable messages
                errorMsg = data.detail.map(err => err.msg || err.type).join(', ');
            } else if (typeof data.detail === 'string') {
                errorMsg = data.detail;
            }
            showError('registerError', errorMsg);
        }
    } catch (error) {
        showError('registerError', 'Cannot connect to server. Make sure backend is running on port 9000');
    }
}

// Login
async function login() {
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    // Validation
    if (!email) {
        showError('loginError', 'Please enter your email');
        return;
    }
    if (!password) {
        showError('loginError', 'Please enter your password');
        return;
    }
    
    // Hide previous error
    document.getElementById('loginError').classList.add('hidden');
    
    try {
        const response = await fetch(`${API_URL}/api/v1/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('dpg_token', authToken);
            loadDashboard();
        } else {
            // Handle validation errors (array format) or simple string errors
            let errorMsg = 'Login failed';
            if (Array.isArray(data.detail)) {
                errorMsg = data.detail.map(err => err.msg || err.type).join(', ');
            } else if (typeof data.detail === 'string') {
                errorMsg = data.detail;
            }
            showError('loginError', errorMsg);
        }
    } catch (error) {
        showError('loginError', 'Cannot connect to server. Make sure backend is running on port 9000');
    }
}

// Logout
function logout() {
    authToken = null;
    localStorage.removeItem('dpg_token');
    showLoginPage();
}

// Load Dashboard
async function loadDashboard() {
    try {
        // Get user info
        const userResponse = await fetch(`${API_URL}/api/v1/auth/me`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (userResponse.ok) {
            currentUser = await userResponse.json();
            document.getElementById('userEmail').textContent = currentUser.email;
            showDashboard();
            loadWallets();
            loadTransactions(); // Auto-load transactions on login
        } else {
            logout();
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
        logout();
    }
}

// Load Wallets
async function loadWallets() {
    try {
        const response = await fetch(`${API_URL}/api/v1/wallets/`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        wallets = await response.json();
        displayWallets();
        populateWalletDropdowns();
    } catch (error) {
        console.error('Error loading wallets:', error);
    }
}

// Display Wallets
function displayWallets() {
    const container = document.getElementById('walletsList');
    
    if (wallets.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No wallets yet. Create your first wallet!</p>';
        return;
    }
    
    container.innerHTML = wallets.map(wallet => `
        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
            <div class="flex justify-between items-center">
                <div>
                    <h4 class="font-bold text-lg">${wallet.currency_code}</h4>
                    <p class="text-sm text-gray-500">${wallet.wallet_type}</p>
                    ${wallet.address ? `<p class="text-xs text-gray-400 mt-1">${wallet.address.substring(0, 20)}...</p>` : ''}
                </div>
                <div class="text-right">
                    <p class="text-2xl font-bold text-green-600">${parseFloat(wallet.balance).toFixed(2)}</p>
                    <p class="text-sm text-gray-500">${wallet.currency_code}</p>
                </div>
            </div>
        </div>
    `).join('');
}

// Populate wallet dropdowns
function populateWalletDropdowns() {
    const depositSelect = document.getElementById('depositWalletId');
    const withdrawSelect = document.getElementById('withdrawWalletId');
    
    const options = wallets.map(w => 
        `<option value="${w.id}">${w.currency_code} (${parseFloat(w.balance).toFixed(2)})</option>`
    ).join('');
    
    depositSelect.innerHTML = options;
    withdrawSelect.innerHTML = options;
}

// Create Wallet Modal
function showCreateWallet() {
    document.getElementById('createWalletModal').classList.remove('hidden');
}

function hideCreateWallet() {
    document.getElementById('createWalletModal').classList.add('hidden');
}

async function createWallet() {
    const currency = document.getElementById('walletCurrency').value;
    const type = (currency === 'USD') ? 'fiat' : 'crypto';
    
    try {
        const response = await fetch(`${API_URL}/api/v1/wallets/create`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                currency_code: currency,
                wallet_type: type
            })
        });
        
        if (response.ok) {
            hideCreateWallet();
            loadWallets();
            alert(`${currency} wallet created successfully!`);
        } else {
            const error = await response.json();
            let errorMsg = 'Failed to create wallet';
            if (Array.isArray(error.detail)) {
                errorMsg = error.detail.map(err => err.msg || err.type).join(', ');
            } else if (typeof error.detail === 'string') {
                errorMsg = error.detail;
            }
            alert(errorMsg);
        }
    } catch (error) {
        alert('Error creating wallet');
    }
}

// Deposit Modal
function showDepositModal() {
    if (wallets.length === 0) {
        alert('Create a wallet first!');
        return;
    }
    document.getElementById('depositModal').classList.remove('hidden');
}

function hideDepositModal() {
    document.getElementById('depositModal').classList.add('hidden');
}

async function deposit() {
    const walletId = document.getElementById('depositWalletId').value;
    const amount = parseFloat(document.getElementById('depositAmount').value);
    
    if (!walletId) {
        alert('Please select a wallet');
        return;
    }
    if (!amount || amount <= 0 || isNaN(amount)) {
        alert('Please enter a valid amount greater than 0');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/v1/transactions/deposit`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                wallet_id: walletId,
                amount: amount,
                description: 'Deposit from frontend',
                reference_id: `DEP_${Date.now()}`
            })
        });
        
        if (response.ok) {
            hideDepositModal();
            document.getElementById('depositAmount').value = '';
            loadWallets();
            loadTransactions(); // Auto-refresh transactions
            alert(`Deposited ${amount} successfully!`);
        } else {
            const error = await response.json();
            let errorMsg = 'Deposit failed';
            if (Array.isArray(error.detail)) {
                errorMsg = error.detail.map(err => err.msg || err.type).join(', ');
            } else if (typeof error.detail === 'string') {
                errorMsg = error.detail;
            }
            alert(errorMsg);
        }
    } catch (error) {
        alert('Error processing deposit');
    }
}

// Withdraw Modal
function showWithdrawModal() {
    if (wallets.length === 0) {
        alert('Create a wallet first!');
        return;
    }
    document.getElementById('withdrawModal').classList.remove('hidden');
}

function hideWithdrawModal() {
    document.getElementById('withdrawModal').classList.add('hidden');
}

async function withdraw() {
    const walletId = document.getElementById('withdrawWalletId').value;
    const amount = parseFloat(document.getElementById('withdrawAmount').value);
    
    if (!walletId) {
        alert('Please select a wallet');
        return;
    }
    if (!amount || amount <= 0 || isNaN(amount)) {
        alert('Please enter a valid amount greater than 0');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/v1/transactions/withdraw`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                wallet_id: walletId,
                amount: amount,
                description: 'Withdrawal from frontend'
            })
        });
        
        if (response.ok) {
            hideWithdrawModal();
            document.getElementById('withdrawAmount').value = '';
            loadWallets();
            loadTransactions(); // Auto-refresh transactions
            alert(`Withdrew ${amount} successfully!`);
        } else {
            const error = await response.json();
            let errorMsg = 'Withdrawal failed';
            if (Array.isArray(error.detail)) {
                errorMsg = error.detail.map(err => err.msg || err.type).join(', ');
            } else if (typeof error.detail === 'string') {
                errorMsg = error.detail;
            }
            alert(errorMsg);
        }
    } catch (error) {
        alert('Error processing withdrawal');
    }
}

// Load Transactions
async function loadTransactions() {
    try {
        const response = await fetch(`${API_URL}/api/v1/transactions/history?limit=20`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const transactions = await response.json();
        displayTransactions(transactions);
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

function displayTransactions(transactions) {
    const section = document.getElementById('transactionsSection');
    const container = document.getElementById('transactionsList');
    
    section.classList.remove('hidden');
    
    if (transactions.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No transactions yet</p>';
        return;
    }
    
    container.innerHTML = `
        <div class="overflow-x-auto">
            <table class="w-full">
                <thead class="bg-gray-100">
                    <tr>
                        <th class="px-4 py-2 text-left">Type</th>
                        <th class="px-4 py-2 text-left">Amount</th>
                        <th class="px-4 py-2 text-left">Fee</th>
                        <th class="px-4 py-2 text-left">Status</th>
                        <th class="px-4 py-2 text-left">Date</th>
                    </tr>
                </thead>
                <tbody>
                    ${transactions.map(tx => `
                        <tr class="border-b hover:bg-gray-50">
                            <td class="px-4 py-3">
                                <span class="px-2 py-1 rounded text-sm ${getTypeColor(tx.type)}">
                                    ${tx.type}
                                </span>
                            </td>
                            <td class="px-4 py-3 font-semibold">${parseFloat(tx.amount).toFixed(2)}</td>
                            <td class="px-4 py-3">${parseFloat(tx.fee).toFixed(2)}</td>
                            <td class="px-4 py-3">
                                <span class="px-2 py-1 rounded text-sm ${getStatusColor(tx.status)}">
                                    ${tx.status}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-sm text-gray-500">
                                ${new Date(tx.created_at).toLocaleString()}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function getTypeColor(type) {
    const colors = {
        'DEPOSIT': 'bg-green-100 text-green-800',
        'WITHDRAWAL': 'bg-red-100 text-red-800',
        'TRANSFER': 'bg-blue-100 text-blue-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
}

function getStatusColor(status) {
    const colors = {
        'COMPLETED': 'bg-green-100 text-green-800',
        'PENDING': 'bg-yellow-100 text-yellow-800',
        'FAILED': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
}

function showError(elementId, message) {
    const errorDiv = document.getElementById(elementId);
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    setTimeout(() => errorDiv.classList.add('hidden'), 5000);
}
