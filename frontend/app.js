// DPG Frontend - JavaScript
const API_URL = 'http://localhost:9000';
let authToken = localStorage.getItem('dpg_token');
let currentUser = null;
let wallets = [];

// Initialize network - if old Mumbai value exists, replace with Sepolia
let savedNetwork = localStorage.getItem('dpg_network');
if (savedNetwork === 'mumbai' || !savedNetwork || !['sepolia', 'amoy'].includes(savedNetwork)) {
    savedNetwork = 'sepolia';
    localStorage.setItem('dpg_network', 'sepolia');
}
let currentNetwork = savedNetwork;

// ============================================
// NETWORK MANAGEMENT
// ============================================

/**
 * Network configurations
 */
const NETWORKS = {
    sepolia: {
        name: 'Sepolia Testnet',
        description: 'Ethereum testnet - Use for ETH transactions',
        currency: 'ETH',
        chainId: 11155111,
        explorer: 'https://sepolia.etherscan.io',
        color: 'blue',
        emoji: '🔵',
        faucets: [
            'https://sepoliafaucet.com/',
            'https://faucet.sepolia.dev/'
        ]
    },
    amoy: {
        name: 'Amoy Testnet',
        description: 'Polygon testnet - Use for MATIC transactions',
        currency: 'MATIC',
        chainId: 80002,
        explorer: 'https://amoy.polygonscan.com',
        color: 'purple',
        emoji: '🟣',
        faucets: [
            'https://faucet.polygon.technology/',
            'https://www.alchemy.com/faucets/polygon-amoy'
        ]
    }
};

/**
 * Switch blockchain network
 */
function switchNetwork() {
    const selector = document.getElementById('networkSelector');
    const newNetwork = selector.value;
    
    if (newNetwork === currentNetwork) return;
    
    // Confirm switch
    const networkInfo = NETWORKS[newNetwork];
    const confirmed = confirm(
        `🔄 Switch Network?\n\n` +
        `From: ${NETWORKS[currentNetwork].name}\n` +
        `To: ${networkInfo.name}\n\n` +
        `This will:\n` +
        `• Change default network for transactions\n` +
        `• Update network display\n` +
        `• Your wallets remain unchanged\n\n` +
        `Continue?`
    );
    
    if (!confirmed) {
        // Reset selector to current network
        selector.value = currentNetwork;
        return;
    }
    
    // Update current network
    currentNetwork = newNetwork;
    localStorage.setItem('dpg_network', newNetwork);
    
    // Update UI
    updateNetworkDisplay();
    
    // Reload wallets to reflect network
    loadWallets();
    
    // Show success message
    showNetworkSwitchSuccess(networkInfo);
}

/**
 * Update network display UI
 */
function updateNetworkDisplay() {
    const networkInfo = NETWORKS[currentNetwork];
    if (!networkInfo) return; // Safety check
    
    // Update banner
    const banner = document.getElementById('networkInfoBanner');
    const nameEl = document.getElementById('networkName');
    const descEl = document.getElementById('networkDescription');
    
    if (banner && nameEl && descEl) {
        // Use fixed Tailwind classes based on network
        if (currentNetwork === 'sepolia') {
            banner.className = 'mt-4 bg-blue-50 border-l-4 border-blue-500 p-3 rounded';
            nameEl.className = 'font-semibold text-blue-800';
            descEl.className = 'text-blue-700 text-xs';
            const icon = banner.querySelector('.fa-info-circle');
            if (icon) icon.className = 'fas fa-info-circle text-blue-500 mt-0.5';
        } else if (currentNetwork === 'amoy') {
            banner.className = 'mt-4 bg-purple-50 border-l-4 border-purple-500 p-3 rounded';
            nameEl.className = 'font-semibold text-purple-800';
            descEl.className = 'text-purple-700 text-xs';
            const icon = banner.querySelector('.fa-info-circle');
            if (icon) icon.className = 'fas fa-info-circle text-purple-500 mt-0.5';
        }
        
        // Update text
        nameEl.textContent = networkInfo.name;
        descEl.textContent = networkInfo.description;
    }
    
    // Update selector
    const selector = document.getElementById('networkSelector');
    if (selector) {
        selector.value = currentNetwork;
    }
}

/**
 * Show network switch success message
 */
function showNetworkSwitchSuccess(networkInfo) {
    const message = `✅ Switched to ${networkInfo.name}!\n\n` +
        `${networkInfo.emoji} Currency: ${networkInfo.currency}\n` +
        `🔗 Chain ID: ${networkInfo.chainId}\n` +
        `🌐 Explorer: ${networkInfo.explorer}\n\n` +
        `Need test ${networkInfo.currency}? Visit:\n${networkInfo.faucets[0]}`;
    
    alert(message);
}

/**
 * Get current network for transactions
 */
function getCurrentNetwork() {
    return currentNetwork;
}

/**
 * Get network info for a currency
 */
function getNetworkForCurrency(currency) {
    if (currency === 'ETH') return 'sepolia';
    if (currency === 'MATIC') return 'amoy';
    return currentNetwork; // Default to current
}

// ============================================
// API HELPER WITH ERROR HANDLING
// ============================================

/**
 * Enhanced fetch wrapper with automatic 401 handling
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @returns {Promise<Response>} - Fetch response
 */
async function apiFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        // Auto-logout only on 401 Unauthorized
        if (response.status === 401) {
            console.warn('⚠️ Session expired (401) - logging out');
            logout();
            throw new Error('Session expired. Please login again.');
        }
        
        return response;
    } catch (error) {
        // Don't logout on network errors
        if (error.message.includes('Session expired')) {
            throw error; // Re-throw 401 error
        }
        console.error('❌ API Error:', error);
        throw error;
    }
}

// ============================================
// FORMATTING UTILITIES
// ============================================

/**
 * Format cryptocurrency amounts with proper precision
 * Shows up to 8 decimal places, removes trailing zeros
 * @param {number|string} amount - The amount to format
 * @param {number} maxDecimals - Maximum decimal places (default: 8)
 * @returns {string} Formatted amount
 */
function formatCrypto(amount, maxDecimals = 8) {
    if (amount === null || amount === undefined || amount === '') return '0';
    
    const num = parseFloat(amount);
    if (isNaN(num)) return '0';
    
    // For very small amounts, show full precision
    if (num > 0 && num < 0.00000001) {
        return num.toExponential(2); // Scientific notation for tiny amounts
    }
    
    // Format with max decimals, then remove trailing zeros
    let formatted = num.toFixed(maxDecimals);
    
    // Remove trailing zeros after decimal point
    formatted = formatted.replace(/\.?0+$/, '');
    
    // If result is empty or just a dot, return "0"
    if (formatted === '' || formatted === '.') return '0';
    
    return formatted;
}

/**
 * Format fiat currency (USD, EUR, etc.)
 * Always shows 2 decimal places
 * @param {number|string} amount - The amount to format
 * @returns {string} Formatted amount with 2 decimals
 */
function formatFiat(amount) {
    if (amount === null || amount === undefined || amount === '') return '0.00';
    const num = parseFloat(amount);
    if (isNaN(num)) return '0.00';
    return num.toFixed(2);
}

/**
 * Shorten blockchain address for display
 * @param {string} address - Full blockchain address
 * @param {number} startChars - Characters to show at start (default: 6)
 * @param {number} endChars - Characters to show at end (default: 4)
 * @returns {string} Shortened address like "0x1234...5678"
 */
function shortenAddress(address, startChars = 6, endChars = 4) {
    if (!address) return '';
    if (address.length <= startChars + endChars) return address;
    return `${address.substring(0, startChars)}...${address.substring(address.length - endChars)}`;
}

/**
 * Format date for display
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
    if (!date) return '';
    const d = new Date(date);
    if (isNaN(d.getTime())) return date;
    return d.toLocaleString();
}

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
    
    // Initialize network display
    updateNetworkDisplay();
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
    stopTransactionAutoRefresh(); // Stop auto-refresh on logout
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
            await loadWallets();
            loadTransactions(); // Auto-load transactions on login (starts auto-refresh)
            
            // Request notification permission for deposit alerts
            requestNotificationPermission();
            
            // Auto-sync all crypto wallets on page load (silent)
            autoSyncAllWallets();
        } else if (userResponse.status === 401) {
            // Only logout on 401 Unauthorized (token expired/invalid)
            console.warn('⚠️ Session expired or invalid token');
            logout();
        } else {
            // For other errors, show error but don't logout
            console.error('❌ Error loading dashboard:', userResponse.status);
            alert('Unable to load dashboard. Please try refreshing the page.');
        }
    } catch (error) {
        console.error('❌ Network error loading dashboard:', error);
        // Don't logout on network errors - just show message
        alert('⚠️ Network error. Check your connection and try again.');
    }
}

// Auto-sync all crypto wallets on page load (silent, no popups)
async function autoSyncAllWallets() {
    const cryptoWallets = wallets.filter(w => 
        w.wallet_type === 'crypto' && w.address
    );
    
    console.log(`🔄 Auto-syncing ${cryptoWallets.length} crypto wallet(s)...`);
    
    for (const wallet of cryptoWallets) {
        try {
            const response = await fetch(`${API_URL}/api/v1/transactions/sync-balance/${wallet.id}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                lastSyncTimes[wallet.id] = new Date();
                console.log(`✅ Synced ${wallet.currency_code}: ${data.old_balance} → ${data.new_balance}`);
            }
        } catch (error) {
            console.debug(`Silent sync error for wallet ${wallet.id}:`, error);
        }
    }
    
    // Reload wallets to show updated balances
    await loadWallets();
    console.log('✅ Auto-sync complete!');
}

// Request notification permission for deposit alerts
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                console.log('✅ Notifications enabled for deposit alerts');
            }
        });
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
    
    const selectedNetwork = getCurrentNetwork();
    console.log('🔍 Display Wallets Debug:', {
        selectedNetwork,
        totalWallets: wallets.length,
        walletCurrencies: wallets.map(w => w.currency_code)
    });
    
    // Filter wallets to only show those matching the current network
    const filteredWallets = wallets.filter(wallet => {
        const walletNetwork = getNetworkForCurrency(wallet.currency_code);
        console.log(`Wallet ${wallet.currency_code} -> network: ${walletNetwork}, matches ${selectedNetwork}: ${walletNetwork === selectedNetwork}`);
        return walletNetwork === selectedNetwork;
    });
    
    // If no wallets for current network, show message
    if (filteredWallets.length === 0) {
        container.innerHTML = `<p class="text-gray-500">No ${NETWORKS[selectedNetwork]?.currency || ''} wallets yet. Create one to get started!</p>`;
        return;
    }
    
    container.innerHTML = filteredWallets.map(wallet => {
        // Use crypto formatting for crypto wallets, fiat formatting for USD
        const isCrypto = wallet.wallet_type === 'crypto' || wallet.currency_code !== 'USD';
        const formattedBalance = isCrypto ? formatCrypto(wallet.balance, 8) : formatFiat(wallet.balance);
        
        return `
        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
            <div class="flex justify-between items-center mb-2">
                <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                        <h4 class="font-bold text-lg">${wallet.currency_code}</h4>
                    </div>
                    <p class="text-sm text-gray-500">${wallet.wallet_type}</p>
                    ${wallet.address ? `<p class="text-xs text-gray-400 mt-1 font-mono">${shortenAddress(wallet.address, 15, 8)}</p>` : ''}
                </div>
                <div class="text-right">
                    <p class="text-2xl font-bold text-green-600">${formattedBalance}</p>
                    <p class="text-sm text-gray-500">${wallet.currency_code}</p>
                </div>
            </div>
            <div class="flex flex-wrap gap-2">
                ${wallet.wallet_type === 'crypto' && wallet.address ? `
                    <button onclick="scanForDeposits('${wallet.id}')" 
                            title="Scan blockchain for incoming deposits (auto-scans every 15s)"
                            class="flex-1 bg-green-500 hover:bg-green-600 text-white text-sm py-1 px-3 rounded transition-all">
                        📥 Scan Deposits
                    </button>
                    <button onclick="syncWalletBalance('${wallet.id}')" 
                            title="Sync balance from blockchain - Last: ${getLastSyncTime(wallet.id)}"
                            class="flex-1 bg-blue-500 hover:bg-blue-600 text-white text-sm py-1 px-3 rounded transition-all">
                        🔄 Sync
                    </button>
                    <button onclick="exportPrivateKey('${wallet.id}')" 
                            title="Export private key (DANGEROUS - keep secret!)"
                            class="flex-1 bg-yellow-500 hover:bg-yellow-600 text-white text-sm py-1 px-3 rounded transition-all">
                        🔑 Export
                    </button>
                ` : ''}
                ${parseFloat(wallet.balance) === 0 ? `
                    <button onclick="deleteWallet('${wallet.id}')" 
                            title="Delete empty wallet"
                            class="flex-1 bg-red-500 hover:bg-red-600 text-white text-sm py-1 px-3 rounded transition-all">
                        🗑️ Delete
                    </button>
                ` : ''}
            </div>
        </div>
        `;
    }).join('');
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
    
    // Set network selector to current network
    const networkSelector = document.getElementById('transferNetwork');
    if (networkSelector) {
        networkSelector.value = getCurrentNetwork();
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
    
    // Disable send button to prevent double-clicking
    const sendButton = document.querySelector('#transferModal button[onclick="transfer()"]');
    if (sendButton) {
        sendButton.disabled = true;
        sendButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Sending...';
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
            alert(`✅ Transaction sent!\n\nTx Hash: ${result.tx_hash}\n\nView on ${network === 'sepolia' ? 'Sepolia Etherscan' : 'Block Explorer'}\n\n⏳ Status will auto-update in 10-15 seconds`);
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
    } finally {
        // Re-enable send button
        if (sendButton) {
            sendButton.disabled = false;
            sendButton.innerHTML = '<i class="fas fa-paper-plane mr-2"></i><span id="transferButtonText">Send</span>';
        }
    }
}

// Auto-refresh interval ID
let transactionRefreshInterval = null;

// Load Transactions
async function loadTransactions() {
    try {
        const response = await fetch(`${API_URL}/api/v1/transactions/history?limit=20`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const transactions = await response.json();
        displayTransactions(transactions);
        
        // Start auto-refresh if not already running
        if (!transactionRefreshInterval) {
            startTransactionAutoRefresh();
        }
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

// Start auto-refreshing transactions every 15 seconds
function startTransactionAutoRefresh() {
    // Clear any existing interval
    if (transactionRefreshInterval) {
        clearInterval(transactionRefreshInterval);
    }
    
    // Auto-refresh every 15 seconds (like MetaMask)
    transactionRefreshInterval = setInterval(async () => {
        try {
            // Auto-scan for deposits on all crypto wallets (silent background check)
            await autoScanDeposits();
            
            // Refresh both wallets and transactions
            await loadWallets();
            
            const response = await fetch(`${API_URL}/api/v1/transactions/history?limit=20`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            
            if (response.ok) {
                const transactions = await response.json();
                displayTransactions(transactions);
                console.log('🔄 Auto-refreshed: wallets & transactions');
            }
        } catch (error) {
            console.error('Auto-refresh error:', error);
        }
    }, 15000); // 15 seconds
    
    console.log('✅ Auto-refresh enabled: wallets & transactions (every 15s)');
}

// Stop auto-refresh
function stopTransactionAutoRefresh() {
    if (transactionRefreshInterval) {
        clearInterval(transactionRefreshInterval);
        transactionRefreshInterval = null;
        console.log('🛑 Auto-refresh stopped');
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
                        <th class="px-4 py-2 text-left">Details</th>
                        <th class="px-4 py-2 text-left">Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${transactions.map(tx => {
                        // Determine if this is a crypto transaction (has network or blockchain fields)
                        const isCrypto = tx.network || tx.tx_hash || (tx.wallet && tx.wallet.currency_code !== 'USD');
                        const formattedAmount = isCrypto ? formatCrypto(tx.amount, 8) : formatFiat(tx.amount);
                        const formattedFee = isCrypto ? formatCrypto(tx.fee, 8) : formatFiat(tx.fee);
                        
                        return `
                        <tr class="border-b hover:bg-gray-50">
                            <td class="px-4 py-3">
                                <span class="px-2 py-1 rounded text-sm ${getTypeColor(tx.type)}">
                                    ${tx.type}
                                </span>
                            </td>
                            <td class="px-4 py-3 font-semibold">${formattedAmount}</td>
                            <td class="px-4 py-3">${formattedFee}</td>
                            <td class="px-4 py-3">
                                <span class="px-2 py-1 rounded text-sm ${getStatusColor(tx.status)}">
                                    ${tx.status}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-sm text-gray-500">
                                ${formatDate(tx.created_at)}
                            </td>
                            <td class="px-4 py-3 text-xs">
                                ${tx.network ? `<span class="text-blue-600">📡 ${tx.network}</span><br>` : ''}
                                ${tx.tx_hash ? `<a href="https://sepolia.etherscan.io/tx/${tx.tx_hash}" target="_blank" class="text-purple-600 hover:underline" title="${tx.tx_hash}">🔗 ${shortenAddress(tx.tx_hash, 8, 6)}</a>` : ''}
                                ${tx.description ? `<span class="text-gray-500">${tx.description}</span>` : ''}
                            </td>
                            <td class="px-4 py-3">
                                <button onclick='viewTransactionReceipt(
                                    "${tx.tx_hash || 'null'}", 
                                    "${tx.type.toLowerCase()}", 
                                    "${formattedAmount}", 
                                    "${tx.status.toLowerCase()}", 
                                    "${tx.created_at}", 
                                    "${formattedFee}",
                                    "${tx.network || ''}"
                                )' class="bg-purple-500 hover:bg-purple-600 text-white px-3 py-1 rounded text-xs transition">
                                    📄 Receipt
                                </button>
                            </td>
                        </tr>
                        `;
                    }).join('')}
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

// Store last sync times for each wallet
const lastSyncTimes = {};

// Sync wallet balance from blockchain with visual feedback
async function syncWalletBalance(walletId) {
    const buttonElement = event?.target;
    const originalContent = buttonElement?.innerHTML;
    
    try {
        // Show loading state
        if (buttonElement) {
            buttonElement.disabled = true;
            buttonElement.innerHTML = '⏳ Syncing...';
            buttonElement.classList.add('opacity-75', 'cursor-wait');
        }
        
        console.log(`🔄 Syncing wallet ${walletId} with blockchain...`);
        
        const response = await fetch(`${API_URL}/api/v1/transactions/sync-balance/${walletId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            // Store sync time
            lastSyncTimes[walletId] = new Date();
            
            // Show success feedback
            if (buttonElement) {
                buttonElement.innerHTML = '✅ Synced!';
                buttonElement.classList.remove('opacity-75', 'cursor-wait');
                buttonElement.classList.add('bg-green-600');
            }
            
            console.log(`✅ Sync complete: ${data.old_balance} → ${data.new_balance}`);
            
            // Reload wallets to show updated balance
            await loadWallets();
            
            // Show notification if balance changed
            const diff = parseFloat(data.difference);
            if (diff !== 0) {
                alert(
                    `✅ Balance Updated!\n\n` +
                    `Old: ${data.old_balance}\n` +
                    `New: ${data.new_balance}\n` +
                    `Change: ${diff > 0 ? '+' : ''}${data.difference}\n\n` +
                    `Network: ${data.network}`
                );
            }
            
            // Reset button after 2 seconds
            setTimeout(() => {
                if (buttonElement) {
                    buttonElement.innerHTML = originalContent;
                    buttonElement.disabled = false;
                    buttonElement.classList.remove('bg-green-600');
                }
            }, 2000);
        } else {
            // Error state
            if (buttonElement) {
                buttonElement.innerHTML = '❌ Failed';
                buttonElement.classList.remove('opacity-75', 'cursor-wait');
                buttonElement.classList.add('bg-red-600');
                
                setTimeout(() => {
                    buttonElement.innerHTML = originalContent;
                    buttonElement.disabled = false;
                    buttonElement.classList.remove('bg-red-600');
                }, 2000);
            }
            alert(`❌ Error: ${data.detail}`);
        }
    } catch (error) {
        console.error('Sync error:', error);
        
        // Error state
        if (buttonElement) {
            buttonElement.innerHTML = '❌ Failed';
            buttonElement.classList.remove('opacity-75', 'cursor-wait');
            buttonElement.classList.add('bg-red-600');
            
            setTimeout(() => {
                buttonElement.innerHTML = originalContent;
                buttonElement.disabled = false;
                buttonElement.classList.remove('bg-red-600');
            }, 2000);
        }
        alert('❌ Failed to sync wallet balance');
    }
}

// Get last sync time for a wallet
function getLastSyncTime(walletId) {
    const syncTime = lastSyncTimes[walletId];
    if (!syncTime) return 'Never synced';
    
    const now = new Date();
    const seconds = Math.floor((now - syncTime) / 1000);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    return `${Math.floor(seconds / 3600)}h ago`;
}

// Export private key for a wallet
async function exportPrivateKey(walletId) {
    // First confirmation - warning about security
    const confirmed = confirm(
        '⚠️ WARNING: SENSITIVE OPERATION!\n\n' +
        'You are about to export your private key.\n\n' +
        '🔐 NEVER share your private key with anyone!\n' +
        '🔐 Anyone with this key has FULL CONTROL of your wallet!\n' +
        '🔐 Store it in a secure location!\n\n' +
        'Do you want to continue?'
    );
    
    if (!confirmed) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/v1/wallets/${walletId}/export-private-key`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            // Show private key in a modal with copy functionality
            showPrivateKeyModal(data);
        } else {
            alert(`❌ Error: ${data.detail}`);
        }
    } catch (error) {
        console.error('Export error:', error);
        alert('❌ Failed to export private key');
    }
}

// Show private key in a secure modal
function showPrivateKeyModal(data) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    modal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div class="mb-4">
                <h3 class="text-2xl font-bold text-red-600 mb-2">🔑 PRIVATE KEY EXPORT</h3>
                <p class="text-sm text-gray-600">
                    ${data.currency} Wallet on ${data.network || 'Blockchain'}
                </p>
            </div>
            
            <!-- Critical Warnings -->
            <div class="bg-red-50 border-2 border-red-400 rounded-lg p-4 mb-4">
                <p class="font-bold text-red-800 mb-2">⚠️ CRITICAL SECURITY WARNINGS:</p>
                <ul class="text-sm text-red-700 list-disc list-inside space-y-1">
                    ${data.warnings ? data.warnings.map(w => `<li>${w}</li>`).join('') : `
                        <li>⚠️ NEVER share your private key with anyone!</li>
                        <li>🔐 Store this key in a secure, offline location</li>
                        <li>💰 Anyone with this key has full control of your wallet</li>
                        <li>🚫 DPG support will NEVER ask for your private key</li>
                        <li>📱 Use this to import into MetaMask or other wallets</li>
                    `}
                </ul>
            </div>
            
            <!-- Network Info -->
            ${data.network ? `
            <div class="bg-blue-50 border border-blue-300 rounded-lg p-4 mb-4">
                <p class="font-bold text-blue-800 mb-2">🌐 Network Information:</p>
                <div class="grid grid-cols-2 gap-2 text-sm">
                    <div>
                        <span class="text-gray-600">Network:</span>
                        <span class="font-semibold text-blue-900 ml-2">${data.network}</span>
                    </div>
                    <div>
                        <span class="text-gray-600">Chain ID:</span>
                        <span class="font-semibold text-blue-900 ml-2">${data.chain_id || 'N/A'}</span>
                    </div>
                    <div>
                        <span class="text-gray-600">Balance:</span>
                        <span class="font-semibold text-blue-900 ml-2">${data.balance} ${data.currency}</span>
                    </div>
                    ${data.explorer_url ? `
                    <div>
                        <a href="${data.explorer_url}/address/${data.address}" target="_blank" 
                           class="text-blue-600 hover:text-blue-800 underline">
                            View on Explorer →
                        </a>
                    </div>
                    ` : ''}
                </div>
            </div>
            ` : ''}
            
            <!-- Wallet Address -->
            <div class="mb-4">
                <label class="block text-sm font-bold mb-2 text-gray-700">📫 Wallet Address:</label>
                <div class="bg-gray-100 p-3 rounded font-mono text-sm break-all border border-gray-300 relative group">
                    <span>${data.address}</span>
                    <button onclick="copyToClipboard('${data.address}', 'Address copied!')" 
                            class="absolute top-2 right-2 bg-white px-2 py-1 rounded text-xs hover:bg-gray-200 border border-gray-300 opacity-0 group-hover:opacity-100 transition-opacity">
                        📋 Copy
                    </button>
                </div>
            </div>
            
            <!-- Private Key -->
            <div class="mb-4">
                <label class="block text-sm font-bold mb-2 text-gray-700">🔐 Private Key:</label>
                <div class="bg-yellow-50 p-4 rounded font-mono text-sm break-all border-2 border-yellow-400 relative">
                    <div class="absolute top-2 right-2 bg-yellow-200 px-2 py-1 rounded text-xs font-bold text-yellow-900 border border-yellow-500">
                        SECRET
                    </div>
                    <span id="privateKeyText" class="pr-20">${data.private_key}</span>
                </div>
            </div>
            
            <!-- Import Instructions -->
            <div class="bg-green-50 border border-green-300 rounded-lg p-4 mb-4">
                <p class="font-bold text-green-800 mb-2">📱 How to Import to MetaMask:</p>
                <ol class="text-sm text-green-700 list-decimal list-inside space-y-1">
                    <li>Open MetaMask and click your account icon</li>
                    <li>Select "Import Account"</li>
                    <li>Paste your private key</li>
                    <li>Make sure you're on the correct network: <strong>${data.network || 'Testnet'}</strong></li>
                </ol>
            </div>
            
            <!-- Action Buttons -->
            <div class="flex flex-col sm:flex-row gap-2">
                <button onclick="copyPrivateKey('${data.private_key}')" 
                        class="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-3 px-4 rounded font-semibold transition-colors">
                    📋 Copy Private Key
                </button>
                <button onclick="downloadWalletBackup(${JSON.stringify(data).replace(/"/g, '&quot;')})" 
                        class="flex-1 bg-purple-500 hover:bg-purple-600 text-white py-3 px-4 rounded font-semibold transition-colors">
                    💾 Download Backup
                </button>
                <button onclick="closePrivateKeyModal()" 
                        class="flex-1 bg-gray-500 hover:bg-gray-600 text-white py-3 px-4 rounded font-semibold transition-colors">
                    ✕ Close
                </button>
            </div>
            
            <!-- Export Timestamp -->
            <div class="mt-4 text-xs text-gray-500 text-center">
                Exported: ${data.export_timestamp || new Date().toISOString()}<br>
                <span class="text-red-600 font-semibold">⚠️ Make sure to save this key before closing!</span>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.id = 'privateKeyModal';
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            const confirmClose = confirm('⚠️ Have you saved your private key?\n\nOnce you close this window, you\'ll need to export again.');
            if (confirmClose) {
                closePrivateKeyModal();
            }
        }
    });
}

// Copy private key to clipboard
function copyPrivateKey(privateKey) {
    navigator.clipboard.writeText(privateKey).then(() => {
        alert('✅ Private key copied to clipboard!\n\n⚠️ Remember to store it securely and clear your clipboard after use.');
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('❌ Failed to copy to clipboard. Please select and copy manually.');
    });
}

// Close private key modal
function closePrivateKeyModal() {
    const modal = document.getElementById('privateKeyModal');
    if (modal) {
        modal.remove();
    }
}

// Download wallet backup as JSON file
function downloadWalletBackup(data) {
    try {
        // Create backup object with all relevant info
        const backup = {
            wallet_id: data.wallet_id,
            currency: data.currency,
            network: data.network || 'Unknown',
            chain_id: data.chain_id,
            address: data.address,
            private_key: data.private_key,
            balance: data.balance,
            export_date: data.export_timestamp || new Date().toISOString(),
            warnings: [
                "⚠️ NEVER share this file with anyone!",
                "🔐 Store this file in a secure, encrypted location",
                "💰 Anyone with access to this file can control your wallet",
                "📱 This file can be used to import your wallet into MetaMask or other wallets"
            ]
        };
        
        // Convert to JSON
        const jsonContent = JSON.stringify(backup, null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json' });
        
        // Create download link
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `DPG_${data.currency}_Wallet_Backup_${new Date().toISOString().split('T')[0]}.json`;
        
        // Trigger download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        alert('✅ Wallet backup downloaded!\n\n⚠️ Store this file securely and never share it with anyone.');
    } catch (error) {
        console.error('Download error:', error);
        alert('❌ Failed to download backup file');
    }
}

// Copy to clipboard helper function
function copyToClipboard(text, successMessage = 'Copied!') {
    navigator.clipboard.writeText(text).then(() => {
        alert(`✅ ${successMessage}`);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('❌ Failed to copy. Please select and copy manually.');
    });
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

// ===== IMPORT WALLET ENHANCEMENTS =====

// Toggle import private key visibility
function toggleImportKeyVisibility() {
    const input = document.getElementById('importPrivateKey');
    const checkbox = document.getElementById('showImportKey');
    input.type = checkbox.checked ? 'text' : 'password';
}

// Verify and preview wallet address from private key
async function verifyImportAddress() {
    const privateKey = document.getElementById('importPrivateKey').value.trim();
    const verificationDiv = document.getElementById('importAddressVerification');
    const previewAddress = document.getElementById('importPreviewAddress');
    
    if (!privateKey || !privateKey.startsWith('0x') || privateKey.length !== 66) {
        verificationDiv.classList.add('hidden');
        return;
    }
    
    try {
        // Use ethers.js-like approach via Web3
        const response = await fetch(`https://cloudflare-eth.com/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'eth_accounts',
                params: [],
                id: 1
            })
        });
        
        // Simple client-side derivation using a technique
        // For security, we'll use backend validation instead
        // Show a placeholder for now
        verificationDiv.classList.remove('hidden');
        previewAddress.textContent = 'Verifying address...';
        
        // Call backend to verify (we can add a verify endpoint later)
        // For now, show generic message
        setTimeout(() => {
            previewAddress.textContent = 'Address will be verified during import';
        }, 500);
        
    } catch (error) {
        console.error('Address verification error:', error);
        verificationDiv.classList.add('hidden');
    }
}

// ===== RECEIVE CRYPTO FEATURE =====

let currentQRCode = null;

// Show receive modal
function showReceiveModal() {
    const modal = document.getElementById('receiveModal');
    const select = document.getElementById('receiveWalletSelect');
    
    // Populate wallet dropdown with crypto wallets only
    const cryptoWallets = wallets.filter(w => w.wallet_type === 'crypto' && w.address);
    
    if (cryptoWallets.length === 0) {
        alert('❌ No crypto wallets available. Please create a crypto wallet first.');
        return;
    }
    
    select.innerHTML = '<option value="">Choose a wallet...</option>' +
        cryptoWallets.map(w => 
            `<option value="${w.id}" data-address="${w.address}" data-currency="${w.currency_code}">
                ${w.currency_code} - ${shortenAddress(w.address, 10, 6)}
            </option>`
        ).join('');
    
    modal.classList.remove('hidden');
    
    // Reset display
    document.getElementById('receiveAddressSection').classList.add('hidden');
}

// Hide receive modal
function hideReceiveModal() {
    document.getElementById('receiveModal').classList.add('hidden');
    if (currentQRCode) {
        document.getElementById('receiveQRCode').innerHTML = '';
        currentQRCode = null;
    }
}

// Display receive address with QR code
function displayReceiveAddress() {
    const select = document.getElementById('receiveWalletSelect');
    const selectedOption = select.options[select.selectedIndex];
    
    if (!selectedOption || !selectedOption.value) {
        document.getElementById('receiveAddressSection').classList.add('hidden');
        return;
    }
    
    const address = selectedOption.getAttribute('data-address');
    const currency = selectedOption.getAttribute('data-currency');
    
    // Show address
    document.getElementById('receiveAddressText').textContent = address;
    document.getElementById('receiveCurrencyName').textContent = currency;
    
    // Set network warning
    const networkMap = {
        'ETH': 'Ethereum (Sepolia Testnet)',
        'MATIC': 'Polygon (Amoy Testnet)',
        'USDT': 'USDT on Ethereum network',
        'USDC': 'USDC on Ethereum network'
    };
    document.getElementById('receiveNetworkWarning').textContent = networkMap[currency] || currency;
    
    // Generate QR code
    const qrContainer = document.getElementById('receiveQRCode');
    qrContainer.innerHTML = ''; // Clear previous QR code
    
    try {
        currentQRCode = new QRCode(qrContainer, {
            text: address,
            width: 200,
            height: 200,
            colorDark: "#5b21b6", // Purple
            colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.H
        });
    } catch (error) {
        console.error('QR Code generation error:', error);
        qrContainer.innerHTML = '<p class="text-red-500 text-sm">QR code generation failed</p>';
    }
    
    // Show section
    document.getElementById('receiveAddressSection').classList.remove('hidden');
}

// Copy receive address to clipboard
function copyReceiveAddress() {
    const address = document.getElementById('receiveAddressText').textContent;
    
    navigator.clipboard.writeText(address).then(() => {
        alert('✅ Address copied to clipboard!\n\nShare this address to receive crypto.');
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('❌ Failed to copy address. Please copy manually.');
    });
}

// Auto-scan for deposits in background (silent, no alerts)
async function autoScanDeposits() {
    try {
        // Only scan crypto wallets with addresses
        const cryptoWallets = wallets.filter(w => 
            w.wallet_type === 'crypto' && w.address && w.currency_code === 'ETH'
        );
        
        if (cryptoWallets.length === 0) return;
        
        // Scan each crypto wallet silently
        for (const wallet of cryptoWallets) {
            try {
                const response = await fetch(`${API_URL}/api/v1/transactions/scan-deposits/${wallet.id}`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${authToken}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (response.ok && data.deposits_found > 0) {
                    console.log(`💰 Auto-detected ${data.deposits_found} new deposit(s) in ${wallet.currency_code} wallet!`);
                    // Show desktop notification if supported
                    if ('Notification' in window && Notification.permission === 'granted') {
                        new Notification('New Deposit Detected!', {
                            body: `Received ${data.total_amount} ${data.currency}`,
                            icon: '/favicon.ico'
                        });
                    }
                }
            } catch (error) {
                console.debug(`Silent scan error for wallet ${wallet.id}:`, error);
            }
        }
    } catch (error) {
        console.debug('Auto-scan error:', error);
    }
}

// Scan for incoming deposits using Etherscan API (manual button)
async function scanForDeposits(walletId) {
    try {
        // Show scanning indicator
        console.log('🔍 Scanning blockchain for deposits...');
        
        const response = await fetch(`${API_URL}/api/v1/transactions/scan-deposits/${walletId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            // Immediately reload wallets and transactions BEFORE showing alert
            console.log('🔄 Refreshing data...');
            await Promise.all([
                loadWallets(),
                loadTransactions()
            ]);
            
            // Then show results
            if (data.deposits_found > 0) {
                const depositList = data.deposits.map(d => 
                    `  💰 ${d.amount} ETH from ${d.from.substring(0, 10)}...`
                ).join('\n');
                
                alert(
                    `✅ ${data.message}\n\n` +
                    `Found ${data.deposits_found} deposit(s):\n${depositList}\n\n` +
                    `Total: ${data.total_amount} ${data.currency}\n` +
                    `New Balance: ${data.new_balance} ${data.currency}`
                );
            } else {
                alert(`${data.message}\n\n${data.note || ''}`);
            }
        } else {
            alert(`❌ Error: ${data.detail}`);
        }
    } catch (error) {
        console.error('Scan error:', error);
        alert('❌ Failed to scan for deposits');
    }
}

// Clean up incorrect deposit transactions
async function cleanupDeposits() {
    const confirmed = confirm(
        '🧹 Clean Up Incorrect Deposits\n\n' +
        'This will delete auto-generated deposit transactions that have wrong amounts.\n\n' +
        'Only deposits WITHOUT blockchain transaction hashes will be removed.\n' +
        'Your real withdrawals and properly tracked transactions will NOT be affected.\n\n' +
        'Continue?'
    );
    
    if (!confirmed) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/v1/transactions/cleanup-deposits`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            alert(`✅ ${data.message}\n\nDeleted: ${data.deleted_count} transaction(s)`);
            // Reload transactions to show cleaned list
            await loadTransactions();
        } else {
            alert(`❌ Error: ${data.detail}`);
        }
    } catch (error) {
        console.error('Cleanup error:', error);
        alert('❌ Failed to cleanup deposits');
    }
}

// ============================================
// PROOF OF RESERVES
// ============================================

async function loadProofOfReserves() {
    try {
        console.log('🔍 Loading proof of reserves...');
        const response = await fetch(`${API_URL}/api/v1/reserves/report`);
        const data = await response.json();
        
        if (response.ok) {
            displayProofOfReserves(data);
            
            // Show section if hidden
            document.getElementById('reservesSection').classList.remove('hidden');
        } else {
            alert('❌ Failed to load proof of reserves');
        }
    } catch (error) {
        console.error('Proof of reserves error:', error);
        document.getElementById('reservesContent').innerHTML = 
            '<p class="text-red-500">Failed to load proof of reserves</p>';
    }
}

function displayProofOfReserves(data) {
    const container = document.getElementById('reservesContent');
    
    // Build solvency indicators
    const solvencyHTML = Object.entries(data.solvency).map(([currency, info]) => {
        const ratio = parseFloat(info.ratio_percent);
        const isHealthy = ratio >= 100;
        const colorClass = isHealthy ? 'text-green-600' : 'text-red-600';
        const bgClass = isHealthy ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200';
        
        return `
            <div class="${bgClass} border-2 rounded-lg p-4">
                <div class="flex justify-between items-center mb-2">
                    <h4 class="text-lg font-bold">${currency}</h4>
                    <span class="${colorClass} text-2xl font-bold">${ratio.toFixed(2)}%</span>
                </div>
                <div class="grid grid-cols-2 gap-2 text-sm">
                    <div>
                        <p class="text-gray-600">Reserves:</p>
                        <p class="font-semibold">${info.reserves} ${currency}</p>
                    </div>
                    <div>
                        <p class="text-gray-600">Liabilities:</p>
                        <p class="font-semibold">${info.liabilities} ${currency}</p>
                    </div>
                </div>
                <div class="mt-2 flex items-center gap-2">
                    ${isHealthy ? 
                        '<span class="text-xs bg-green-200 text-green-800 px-2 py-1 rounded">✅ Fully Reserved</span>' :
                        '<span class="text-xs bg-red-200 text-red-800 px-2 py-1 rounded">⚠️ Under-Reserved</span>'
                    }
                </div>
            </div>
        `;
    }).join('');
    
    // Build Merkle tree info
    const merkleHTML = Object.entries(data.merkle_trees).map(([currency, tree]) => {
        if (!tree.merkle_root) return '';
        
        return `
            <div class="bg-gray-50 border rounded-lg p-4">
                <h5 class="font-bold mb-2">${currency} Merkle Tree</h5>
                <div class="space-y-1 text-xs">
                    <p><span class="font-semibold">Root:</span> <code class="bg-white px-2 py-1 rounded">${tree.merkle_root.substring(0, 32)}...</code></p>
                    <p><span class="font-semibold">Users:</span> ${tree.total_users}</p>
                    <p><span class="font-semibold">Total Balance:</span> ${tree.total_balance} ${currency}</p>
                    <p><span class="font-semibold">Tree Height:</span> ${tree.tree_height}</p>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = `
        <!-- Summary Stats -->
        <div class="bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200 rounded-lg p-6 mb-4">
            <h4 class="text-xl font-bold mb-4">📊 Platform Statistics</h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                    <p class="text-gray-600 text-sm">Total Users</p>
                    <p class="text-2xl font-bold text-purple-600">${data.total_users}</p>
                </div>
                <div>
                    <p class="text-gray-600 text-sm">Total Wallets</p>
                    <p class="text-2xl font-bold text-purple-600">${data.total_wallets}</p>
                </div>
                <div>
                    <p class="text-gray-600 text-sm">Last Updated</p>
                    <p class="text-sm font-semibold text-gray-700">${new Date(data.timestamp).toLocaleString()}</p>
                </div>
                <div>
                    <p class="text-gray-600 text-sm">Audit Method</p>
                    <p class="text-sm font-semibold text-gray-700">${data.attestation.method}</p>
                </div>
            </div>
        </div>
        
        <!-- Solvency Ratios -->
        <div class="mb-4">
            <h4 class="text-lg font-bold mb-3">💰 Solvency Ratios</h4>
            <div class="grid md:grid-cols-2 gap-4">
                ${solvencyHTML}
            </div>
        </div>
        
        <!-- Merkle Trees -->
        <div class="mb-4">
            <h4 class="text-lg font-bold mb-3">🌳 Merkle Tree Verification</h4>
            <div class="grid md:grid-cols-2 gap-4">
                ${merkleHTML}
            </div>
            <p class="text-xs text-gray-500 mt-2">
                <i class="fas fa-info-circle"></i> Merkle trees provide cryptographic proof that user balances are included in reserves
            </p>
        </div>
        
        ${data.onchain_verification ? `
        <!-- On-Chain Verification -->
        <div class="mb-4">
            <h4 class="text-lg font-bold mb-3">⛓️ On-Chain Verification</h4>
            <div class="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-lg p-4 mb-3">
                <div class="flex items-center gap-2 mb-2">
                    <span class="text-2xl">✅</span>
                    <h5 class="font-bold text-green-900">Blockchain Verified</h5>
                </div>
                <p class="text-sm text-green-800 mb-2">
                    Reserve balances verified directly from ${data.onchain_verification.network} blockchain
                </p>
                <p class="text-xs text-green-700">
                    <i class="fas fa-clock"></i> Verified at: ${new Date(data.onchain_verification.verified_at).toLocaleString()}
                </p>
            </div>
            
            <div class="grid md:grid-cols-2 gap-4">
                ${Object.entries(data.onchain_verification.comparison).map(([currency, comp]) => {
                    const matchPercent = parseFloat(comp.match_percent);
                    const isVerified = comp.status === 'VERIFIED';
                    const bgClass = isVerified ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200';
                    const textClass = isVerified ? 'text-green-800' : 'text-yellow-800';
                    
                    return `
                        <div class="${bgClass} border-2 rounded-lg p-4">
                            <div class="flex justify-between items-center mb-2">
                                <h5 class="font-bold">${currency}</h5>
                                <span class="${textClass} font-bold">${comp.status}</span>
                            </div>
                            <div class="space-y-2 text-sm">
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Database:</span>
                                    <span class="font-semibold">${comp.database_balance}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">On-Chain:</span>
                                    <span class="font-semibold">${comp.onchain_balance}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-gray-600">Match:</span>
                                    <span class="font-bold ${textClass}">${matchPercent.toFixed(2)}%</span>
                                </div>
                            </div>
                            <div class="mt-3 pt-3 border-t border-gray-300">
                                <p class="text-xs text-gray-600 mb-1">Reserve Wallet:</p>
                                ${comp.reserve_wallets.map(addr => `
                                    <a href="https://sepolia.etherscan.io/address/${addr}" 
                                       target="_blank" 
                                       class="text-xs text-blue-600 hover:underline block truncate">
                                        ${addr}
                                    </a>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
            <p class="text-xs text-gray-500 mt-2">
                <i class="fas fa-external-link-alt"></i> Click wallet addresses to verify balances on Etherscan
            </p>
        </div>
        ` : ''}
        
        <!-- Transparency Note -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h5 class="font-bold text-blue-900 mb-2">🔍 Full Transparency</h5>
            <p class="text-sm text-blue-800">
                This proof of reserves report is publicly available and updated in real-time. 
                It demonstrates that the platform maintains 100% reserves for all user funds. 
                Anyone can verify the Merkle tree roots and check reserve wallet addresses on the blockchain.
            </p>
        </div>
    `;
}

// ============================================
// TRANSACTION RECEIPT
// ============================================

function viewTransactionReceipt(txHash, type, amount, status, date, fee, network) {
    const modal = document.getElementById('transactionReceiptModal');
    const content = document.getElementById('receiptContent');
    
    // Normalize network (handle empty strings and null)
    const normalizedNetwork = network && network.trim() !== '' ? network.toLowerCase() : 'sepolia';
    
    // Determine explorer URL
    const explorerMap = {
        'sepolia': `https://sepolia.etherscan.io/tx/${txHash}`,
        'ethereum': `https://etherscan.io/tx/${txHash}`,
        'amoy': `https://amoy.polygonscan.com/tx/${txHash}`,
        'polygon': `https://polygonscan.com/tx/${txHash}`
    };
    
    const explorerUrl = explorerMap[normalizedNetwork] || `https://sepolia.etherscan.io/tx/${txHash}`;
    const hasBlockchain = txHash && txHash !== 'null' && txHash !== '';
    
    content.innerHTML = `
        <div class="space-y-6">
            <!-- DPG Elegant Branding Header -->
            <div class="bg-gradient-to-br from-purple-600 via-purple-500 to-blue-500 text-white py-8 px-6 rounded-t-lg -mx-8 -mt-8 mb-6 shadow-2xl">
                <div class="flex items-center justify-center gap-3 mb-3">
                    <div class="bg-white bg-opacity-20 p-3 rounded-lg backdrop-blur-sm">
                        <span class="text-4xl">💳</span>
                    </div>
                    <div class="text-left">
                        <h2 class="text-4xl font-bold tracking-wider">DPG</h2>
                        <p class="text-sm opacity-90 tracking-wide">Digital Payment Gateway</p>
                    </div>
                </div>
                <div class="flex items-center justify-center gap-2 text-xs opacity-90 mt-3">
                    <span>🔒 Secure</span>
                    <span>•</span>
                    <span>⛓️ Transparent</span>
                    <span>•</span>
                    <span>🌐 Decentralized</span>
                </div>
            </div>
            
            <!-- Transaction Type Header -->
            <div class="text-center pb-4 border-b-2 border-gray-200">
                <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br ${
                    type === 'deposit' ? 'from-green-400 to-emerald-500' :
                    type === 'withdrawal' ? 'from-red-400 to-pink-500' :
                    'from-blue-400 to-indigo-500'
                } rounded-full mb-3 shadow-lg">
                    <span class="text-4xl">${type === 'deposit' ? '📥' : type === 'withdrawal' ? '📤' : '🔄'}</span>
                </div>
                <h4 class="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                    ${type.toUpperCase()} RECEIPT
                </h4>
                <p class="text-sm text-gray-500 mt-2">
                    <i class="fas fa-calendar-alt mr-1"></i>${new Date(date).toLocaleString()}
                </p>
            </div>
            
            <!-- Amount -->
            <div class="bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 border-2 border-purple-200 rounded-xl p-8 text-center shadow-lg">
                <p class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Transaction Amount</p>
                <p class="text-5xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
                    ${amount}
                </p>
                ${fee > 0 ? `
                    <div class="mt-4 pt-4 border-t border-gray-300">
                        <p class="text-xs text-gray-500 uppercase tracking-wide">Network Fee</p>
                        <p class="text-lg font-semibold text-gray-700">${fee}</p>
                    </div>
                ` : ''}
            </div>
            
            <!-- Status -->
            <div class="flex items-center justify-center gap-3">
                <div class="px-6 py-3 rounded-full text-lg font-bold shadow-lg ${
                    status === 'completed' ? 'bg-gradient-to-r from-green-400 to-emerald-500 text-white' :
                    status === 'pending' ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white' :
                    'bg-gradient-to-r from-red-400 to-pink-500 text-white'
                }">
                    <span class="mr-2">${status === 'completed' ? '✅' : status === 'pending' ? '⏳' : '❌'}</span>
                    ${status.toUpperCase()}
                </div>
            </div>
            
            ${hasBlockchain ? `
                <!-- Transaction Hash -->
                <div class="bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200 rounded-xl p-5 shadow-sm">
                    <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <i class="fas fa-fingerprint"></i>Transaction Hash
                    </p>
                    <div class="flex items-center gap-2">
                        <code class="flex-1 bg-white px-4 py-3 rounded-lg text-xs break-all border border-gray-300 font-mono text-gray-700">${txHash}</code>
                        <button onclick="copyToClipboard('${txHash}')" 
                                class="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white px-4 py-3 rounded-lg text-sm font-semibold shadow-md transition-all">
                            <i class="fas fa-copy mr-1"></i>Copy
                        </button>
                    </div>
                </div>
                
                <!-- QR Code -->
                <div class="text-center bg-white p-6 rounded-xl border-2 border-gray-200 shadow-sm">
                    <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4 flex items-center justify-center gap-2">
                        <i class="fas fa-qrcode"></i>Transaction QR Code
                    </p>
                    <div id="receiptQRCode" class="inline-block bg-white p-3 rounded-lg border-4 border-purple-200"></div>
                    <p class="text-xs text-gray-500 mt-3">Scan to view on blockchain explorer</p>
                </div>
                
                <!-- Blockchain Explorer -->
                <div class="text-center">
                    <a href="${explorerUrl}" target="_blank" rel="noopener noreferrer"
                       class="inline-flex items-center gap-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-8 py-4 rounded-xl font-bold shadow-lg transition-all transform hover:scale-105">
                        <i class="fas fa-external-link-alt"></i>
                        View on ${normalizedNetwork === 'amoy' ? 'Polygonscan' : 'Etherscan'}
                    </a>
                </div>
            ` : ''}
            
            <!-- Actions -->
            <div class="flex gap-3 pt-6 border-t-2 border-gray-200">
                <button onclick="printReceipt()" 
                        class="flex-1 bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-800 hover:to-gray-900 text-white py-3 rounded-xl font-bold shadow-lg transition-all transform hover:scale-105 flex items-center justify-center gap-2">
                    <i class="fas fa-print"></i>Print Receipt
                </button>
                <button onclick="closeTransactionReceipt()" 
                        class="flex-1 bg-gradient-to-r from-gray-300 to-gray-400 hover:from-gray-400 hover:to-gray-500 text-gray-800 py-3 rounded-xl font-bold shadow-lg transition-all transform hover:scale-105">
                    Close
                </button>
            </div>
            
            <!-- Elegant DPG Footer Branding -->
            <div class="text-center pt-6 pb-2">
                <div class="inline-block bg-gradient-to-r from-purple-50 to-blue-50 px-8 py-4 rounded-xl border border-gray-200 shadow-sm">
                    <div class="flex items-center justify-center gap-3 mb-2">
                        <div class="bg-gradient-to-br from-purple-600 to-blue-600 p-2 rounded-lg">
                            <span class="text-2xl">💳</span>
                        </div>
                        <div class="text-left">
                            <p class="text-lg font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">DPG</p>
                            <p class="text-xs text-gray-600">Digital Payment Gateway</p>
                        </div>
                    </div>
                    <div class="flex items-center justify-center gap-2 text-xs text-gray-500 mt-3 pt-3 border-t border-gray-300">
                        <i class="fas fa-shield-alt text-green-500"></i>
                        <span>Secure</span>
                        <span>•</span>
                        <i class="fas fa-link text-blue-500"></i>
                        <span>Transparent</span>
                        <span>•</span>
                        <i class="fas fa-globe text-purple-500"></i>
                        <span>Decentralized</span>
                    </div>
                    <p class="text-xs text-gray-400 mt-2">© 2025 DPG. All rights reserved.</p>
                </div>
            </div>
        </div>
    `;
    
    // Generate QR code if blockchain transaction
    if (hasBlockchain) {
        setTimeout(() => {
            const qrContainer = document.getElementById('receiptQRCode');
            if (qrContainer) {
                try {
                    new QRCode(qrContainer, {
                        text: explorerUrl,
                        width: 150,
                        height: 150,
                        colorDark: "#5b21b6",
                        colorLight: "#ffffff",
                        correctLevel: QRCode.CorrectLevel.H
                    });
                } catch (error) {
                    console.error('QR generation error:', error);
                }
            }
        }, 100);
    }
    
    modal.classList.remove('hidden');
}

function closeTransactionReceipt() {
    document.getElementById('transactionReceiptModal').classList.add('hidden');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('✅ Copied to clipboard!');
    }).catch(err => {
        console.error('Copy failed:', err);
        alert('❌ Failed to copy');
    });
}

function printReceipt() {
    window.print();
}


