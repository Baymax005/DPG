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
            <div class="flex justify-between items-center mb-2">
                <div class="flex-1">
                    <h4 class="font-bold text-lg">${wallet.currency_code}</h4>
                    <p class="text-sm text-gray-500">${wallet.wallet_type}</p>
                    ${wallet.address ? `<p class="text-xs text-gray-400 mt-1 font-mono">${wallet.address.substring(0, 15)}...${wallet.address.substring(wallet.address.length - 8)}</p>` : ''}
                </div>
                <div class="text-right">
                    <p class="text-2xl font-bold text-green-600">${parseFloat(wallet.balance).toFixed(4)}</p>
                    <p class="text-sm text-gray-500">${wallet.currency_code}</p>
                </div>
            </div>
            <div class="flex gap-2">
                ${wallet.wallet_type === 'crypto' && wallet.address ? `
                    <button onclick="syncWalletBalance('${wallet.id}')" 
                            class="flex-1 bg-blue-500 hover:bg-blue-600 text-white text-sm py-1 px-3 rounded">
                        🔄 Sync Balance
                    </button>
                ` : ''}
                ${parseFloat(wallet.balance) === 0 ? `
                    <button onclick="deleteWallet('${wallet.id}')" 
                            class="flex-1 bg-red-500 hover:bg-red-600 text-white text-sm py-1 px-3 rounded">
                        🗑️ Delete
                    </button>
                ` : ''}
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

// Import Wallet Modal
function showImportWallet() {
    document.getElementById('importWalletModal').classList.remove('hidden');
}

function hideImportWallet() {
    document.getElementById('importWalletModal').classList.add('hidden');
    document.getElementById('importPrivateKey').value = '';
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

// Import Wallet function
async function importWallet() {
    const currency = document.getElementById('importWalletCurrency').value;
    const privateKey = document.getElementById('importPrivateKey').value.trim();
    
    if (!privateKey) {
        alert('Please enter your private key');
        return;
    }
    
    if (!privateKey.startsWith('0x') || privateKey.length !== 66) {
        alert('Invalid private key format. Must start with 0x and be 66 characters long.');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/v1/wallets/import`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                currency_code: currency,
                private_key: privateKey
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            hideImportWallet();
            await loadWallets();
            alert(`✅ Wallet imported successfully!\n\nAddress: ${data.address}\nBalance: ${data.balance} ${currency}`);
        } else {
            alert(`❌ ${data.detail || 'Failed to import wallet'}`);
        }
    } catch (error) {
        console.error('Import error:', error);
        alert('❌ Error importing wallet. Check your private key and try again.');
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

// Transfer Modal
function showTransferModal() {
    if (wallets.length === 0) {
        alert('Create at least one wallet first!');
        return;
    }
    
    // Populate from wallet dropdown
    const fromSelect = document.getElementById('transferFromWallet');
    fromSelect.innerHTML = '<option value="">Select source wallet...</option>';
    wallets.forEach(wallet => {
        const option = document.createElement('option');
        option.value = wallet.id;
        // Use both currency_code and currency fields
        const currency = wallet.currency_code || wallet.currency;
        option.dataset.currency = currency;
        option.textContent = `${currency} - Balance: ${wallet.balance}`;
        fromSelect.appendChild(option);
    });
    
    // Add event listener for "From" wallet change
    fromSelect.onchange = function() {
        updateToWalletDropdown();
        updateTransferFee();
    };
    
    // Add event listener for amount change
    const amountInput = document.getElementById('transferAmount');
    amountInput.oninput = function() {
        updateTransferFee();
    };
    
    // Reset to internal mode
    switchTransferMode('internal');
    
    document.getElementById('transferModal').classList.remove('hidden');
}

function updateToWalletDropdown() {
    const fromSelect = document.getElementById('transferFromWallet');
    const selectedFromWalletId = fromSelect.value; // Keep as string (UUIDs)
    const toSelect = document.getElementById('transferToWallet');
    
    // Filter wallets (excluding the selected from wallet)
    toSelect.innerHTML = '<option value="">Select destination wallet...</option>';
    
    if (selectedFromWalletId) {
        wallets.forEach(wallet => {
            // Show all wallets except the selected one
            if (String(wallet.id) !== String(selectedFromWalletId)) {
                const option = document.createElement('option');
                option.value = wallet.id;
                const currency = wallet.currency_code || wallet.currency;
                option.textContent = `${currency} - Balance: ${wallet.balance}`;
                toSelect.appendChild(option);
            }
        });
    }
}

function updateTransferFee() {
    const mode = document.getElementById('internalModeFields').classList.contains('hidden') ? 'external' : 'internal';
    const amountInput = document.getElementById('transferAmount');
    const amount = parseFloat(amountInput.value) || 0;
    
    if (mode === 'internal') {
        document.getElementById('transferFeeInfo').textContent = 
            `✅ FREE internal transfer! No fees charged.`;
        document.getElementById('feeInfoBox').className = 'bg-green-50 border border-green-200 rounded-lg p-3';
    } else {
        // External mode - show testnet fees
        const fromWallet = wallets.find(w => String(w.id) === document.getElementById('transferFromWallet').value);
        const currency = fromWallet ? (fromWallet.currency_code || fromWallet.currency) : '';
        
        if (currency === 'ETH' || currency === 'USDT' || currency === 'USDC') {
            document.getElementById('transferFeeInfo').textContent = 
                `⚡ Testnet Gas Fee: FREE (Sepolia) • Mainnet: ~$2-5`;
        } else {
            document.getElementById('transferFeeInfo').textContent = 
                `💰 Network Fee: Varies by blockchain`;
        }
        document.getElementById('feeInfoBox').className = 'bg-blue-50 border border-blue-200 rounded-lg p-3';
    }
}

// Switch between Internal and External transfer modes
let currentTransferMode = 'internal';

function switchTransferMode(mode) {
    currentTransferMode = mode;
    
    const internalFields = document.getElementById('internalModeFields');
    const externalFields = document.getElementById('externalModeFields');
    const internalBtn = document.getElementById('internalModeBtn');
    const externalBtn = document.getElementById('externalModeBtn');
    const buttonText = document.getElementById('transferButtonText');
    
    if (mode === 'internal') {
        // Show internal mode
        internalFields.classList.remove('hidden');
        externalFields.classList.add('hidden');
        
        // Update button styles
        internalBtn.className = 'flex-1 py-2 px-4 rounded-md font-semibold transition-all bg-white text-purple-600 shadow';
        externalBtn.className = 'flex-1 py-2 px-4 rounded-md font-semibold transition-all text-gray-600';
        
        buttonText.textContent = 'Transfer';
    } else {
        // Show external mode
        internalFields.classList.add('hidden');
        externalFields.classList.remove('hidden');
        
        // Update button styles
        internalBtn.className = 'flex-1 py-2 px-4 rounded-md font-semibold transition-all text-gray-600';
        externalBtn.className = 'flex-1 py-2 px-4 rounded-md font-semibold transition-all bg-white text-purple-600 shadow';
        
        buttonText.textContent = 'Send';
    }
    
    updateTransferFee();
}

// Validate Ethereum address
function isValidEthereumAddress(address) {
    return /^0x[a-fA-F0-9]{40}$/.test(address);
}

// Validate Bitcoin address (basic validation)
function isValidBitcoinAddress(address) {
    // P2PKH (1...), P2SH (3...), Bech32 (bc1...)
    return /^(1|3|bc1)[a-zA-HJ-NP-Z0-9]{25,62}$/.test(address);
}

// Validate address based on currency
function validateAddress(address, currency) {
    if (!address || address.trim() === '') {
        return { valid: false, message: 'Please enter a recipient address' };
    }
    
    if (currency === 'ETH' || currency === 'USDT' || currency === 'USDC') {
        if (isValidEthereumAddress(address)) {
            return { valid: true, message: '' };
        }
        return { valid: false, message: 'Invalid Ethereum address. Must start with 0x and be 42 characters long.' };
    } else if (currency === 'BTC') {
        if (isValidBitcoinAddress(address)) {
            return { valid: true, message: '' };
        }
        return { valid: false, message: 'Invalid Bitcoin address format.' };
    }
    
    return { valid: false, message: 'Address validation not available for this currency yet.' };
}

function hideTransferModal() {
    document.getElementById('transferModal').classList.add('hidden');
    document.getElementById('transferFromWallet').value = '';
    document.getElementById('transferToWallet').value = '';
    document.getElementById('transferToAddress').value = '';
    document.getElementById('transferAmount').value = '';
    document.getElementById('transferDescription').value = '';
    currentTransferMode = 'internal';
}

async function transfer() {
    const fromWalletId = document.getElementById('transferFromWallet').value;
    const amount = parseFloat(document.getElementById('transferAmount').value);
    const description = document.getElementById('transferDescription').value || 'Transfer';
    
    // Validation
    if (!fromWalletId) {
        alert('Please select a source wallet');
        return;
    }
    if (!amount || amount <= 0 || isNaN(amount)) {
        alert('Please enter a valid amount greater than 0');
        return;
    }
    
    // Get source wallet info
    const fromWallet = wallets.find(w => String(w.id) === String(fromWalletId));
    const currency = fromWallet ? (fromWallet.currency_code || fromWallet.currency) : '';
    
    if (currentTransferMode === 'internal') {
        // Internal transfer (between user's wallets)
        await transferInternal(fromWalletId, amount, description);
    } else {
        // External send (to blockchain address)
        await sendExternal(fromWalletId, amount, description, currency);
    }
}

async function transferInternal(fromWalletId, amount, description) {
    const toWalletId = document.getElementById('transferToWallet').value;
    
    if (!toWalletId) {
        alert('Please select a destination wallet');
        return;
    }
    if (fromWalletId === toWalletId) {
        alert('Cannot transfer to the same wallet');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/v1/transactions/transfer`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                from_wallet_id: fromWalletId,
                to_wallet_id: toWalletId,
                amount: amount,
                description: description
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            hideTransferModal();
            loadWallets();
            loadTransactions();
            alert(`✅ Transfer successful! ${amount} transferred between your wallets.`);
        } else {
            const error = await response.json();
            let errorMsg = 'Transfer failed';
            if (Array.isArray(error.detail)) {
                errorMsg = error.detail.map(err => err.msg || err.type).join(', ');
            } else if (typeof error.detail === 'string') {
                errorMsg = error.detail;
            }
            alert(errorMsg);
        }
    } catch (error) {
        console.error('Transfer error:', error);
        alert('Error processing transfer');
    }
}

async function sendExternal(fromWalletId, amount, description, currency) {
    const toAddress = document.getElementById('transferToAddress').value.trim();
    const network = document.getElementById('transferNetwork').value;
    
    // Validate address
    const validation = validateAddress(toAddress, currency);
    if (!validation.valid) {
        alert(validation.message);
        return;
    }
    
    // Confirm before sending
    const confirmMsg = `⚠️ SEND TO BLOCKCHAIN\n\n` +
        `From: ${currency} Wallet\n` +
        `To: ${toAddress.substring(0, 10)}...${toAddress.substring(toAddress.length - 8)}\n` +
        `Amount: ${amount} ${currency}\n` +
        `Network: ${network}\n\n` +
        `This will send a REAL blockchain transaction!\n` +
        `Are you sure?`;
    
    if (!confirm(confirmMsg)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/v1/transactions/send`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                wallet_id: fromWalletId,
                to_address: toAddress,
                amount: amount,
                network: network,
                description: description
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            hideTransferModal();
            loadWallets();
            loadTransactions();
            alert(`✅ Transaction sent!\n\nTx Hash: ${result.tx_hash}\n\nView on ${network === 'sepolia' ? 'Sepolia Etherscan' : 'Block Explorer'}`);
        } else {
            const error = await response.json();
            let errorMsg = 'Send failed';
            if (Array.isArray(error.detail)) {
                errorMsg = error.detail.map(err => err.msg || err.type).join(', ');
            } else if (typeof error.detail === 'string') {
                errorMsg = error.detail;
            }
            alert('❌ ' + errorMsg);
        }
    } catch (error) {
        console.error('Send error:', error);
        alert('Error processing blockchain transaction');
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

// Sync wallet balance from blockchain
async function syncWalletBalance(walletId) {
    try {
        const response = await fetch(`${API_URL}/api/v1/wallets/${walletId}/sync-blockchain`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            alert(`✅ ${data.message}\n\nAddress: ${data.address}\nBalance: ${data.balance} ${data.currency}\nNetwork: ${data.network}`);
            // Reload wallets to show updated balance
            await loadWallets();
        } else {
            alert(`❌ Error: ${data.detail}`);
        }
    } catch (error) {
        console.error('Sync error:', error);
        alert('❌ Failed to sync wallet balance');
    }
}

// Delete wallet
async function deleteWallet(walletId) {
    if (!confirm('Are you sure you want to delete this wallet? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/v1/wallets/${walletId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            alert('✅ Wallet deleted successfully');
            await loadWallets();
        } else {
            const data = await response.json();
            alert(`❌ ${data.detail || 'Failed to delete wallet'}`);
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert(`❌ Failed to delete wallet: ${error.message}`);
    }
}
