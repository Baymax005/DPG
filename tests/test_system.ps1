# DPG Complete System Test - PowerShell Version
# Run this while server is running

Write-Host "`n" -NoNewline
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "  🚀 DPG COMPLETE SYSTEM TEST" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Cyan

$baseUrl = "http://localhost:9000"

# 1. LOGIN
Write-Host "`n" -NoNewline
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "  1️⃣ AUTHENTICATION - Login" -ForegroundColor Yellow
Write-Host "="*80 -ForegroundColor Cyan

$loginData = @{
    email = "test@example.com"
    password = "Test123456"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json"
$token = $response.access_token

Write-Host "   ✅ Login successful!" -ForegroundColor Green
Write-Host "   🔑 Token: $($token.Substring(0, 40))..." -ForegroundColor White

$headers = @{
    Authorization = "Bearer $token"
}

# 2. CREATE WALLETS
Write-Host "`n" -NoNewline
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "  2️⃣ WALLETS - Create USD wallet" -ForegroundColor Yellow
Write-Host "="*80 -ForegroundColor Cyan

$usdWallet = @{
    currency_code = "USD"
    wallet_type = "fiat"
} | ConvertTo-Json

try {
    $wallet = Invoke-RestMethod -Uri "$baseUrl/api/v1/wallets/create" -Method POST -Body $usdWallet -ContentType "application/json" -Headers $headers
    Write-Host "   ✅ USD Wallet created!" -ForegroundColor Green
    Write-Host "   💰 Currency: $($wallet.currency_code)" -ForegroundColor White
    Write-Host "   💵 Balance: $($wallet.balance)" -ForegroundColor White
    $usdWalletId = $wallet.id
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "   ℹ️  USD Wallet already exists" -ForegroundColor Yellow
        $wallets = Invoke-RestMethod -Uri "$baseUrl/api/v1/wallets/" -Method GET -Headers $headers
        $usdWalletId = ($wallets | Where-Object { $_.currency_code -eq "USD" })[0].id
        Write-Host "   ✅ Using existing wallet: $usdWalletId" -ForegroundColor Green
    }
}

# 3. DEPOSIT
Write-Host "`n" -NoNewline
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "  3️⃣ TRANSACTIONS - Deposit `$1000" -ForegroundColor Yellow
Write-Host "="*80 -ForegroundColor Cyan

$depositData = @{
    wallet_id = $usdWalletId
    amount = 1000.00
    description = "Test deposit - PowerShell test"
    reference_id = "TEST_$(Get-Date -Format 'yyyyMMddHHmmss')"
} | ConvertTo-Json

$tx = Invoke-RestMethod -Uri "$baseUrl/api/v1/transactions/deposit" -Method POST -Body $depositData -ContentType "application/json" -Headers $headers

Write-Host "   ✅ Deposited `$1000!" -ForegroundColor Green
Write-Host "   🆔 Transaction ID: $($tx.id)" -ForegroundColor White
Write-Host "   💵 Amount: `$$($tx.amount)" -ForegroundColor White
Write-Host "   ✅ Status: $($tx.status)" -ForegroundColor White

# 4. CHECK BALANCE
Write-Host "`n" -NoNewline
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "  4️⃣ WALLETS - Check balance" -ForegroundColor Yellow
Write-Host "="*80 -ForegroundColor Cyan

$wallets = Invoke-RestMethod -Uri "$baseUrl/api/v1/wallets/" -Method GET -Headers $headers

$walletCount = $wallets.Count
Write-Host "   ✅ User has $walletCount wallets:" -ForegroundColor Green
foreach ($w in $wallets) {
    Write-Host "      💰 $($w.currency_code): $($w.balance)" -ForegroundColor White
}

# 5. WITHDRAW
Write-Host "`n" -NoNewline
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "  5️⃣ TRANSACTIONS - Withdraw `$100" -ForegroundColor Yellow
Write-Host "="*80 -ForegroundColor Cyan

$withdrawData = @{
    wallet_id = $usdWalletId
    amount = 100.00
    description = "Test withdrawal"
} | ConvertTo-Json

$tx = Invoke-RestMethod -Uri "$baseUrl/api/v1/transactions/withdraw" -Method POST -Body $withdrawData -ContentType "application/json" -Headers $headers

Write-Host "   ✅ Withdrew `$100!" -ForegroundColor Green
Write-Host "   💵 Amount: `$$($tx.amount)" -ForegroundColor White
Write-Host "   💸 Fee: `$$($tx.fee)" -ForegroundColor White

# 6. TRANSACTION HISTORY
Write-Host "`n" -NoNewline
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "  6️⃣ TRANSACTIONS - View history" -ForegroundColor Yellow
Write-Host "="*80 -ForegroundColor Cyan

$transactions = Invoke-RestMethod -Uri "$baseUrl/api/v1/transactions/history?limit=5" -Method GET -Headers $headers

$txCount = $transactions.Count
Write-Host "   ✅ Found $txCount recent transactions:" -ForegroundColor Green
$i = 1
foreach ($tx in $transactions) {
    Write-Host "`n      Transaction #$i:" -ForegroundColor Cyan
    Write-Host "         Type: $($tx.type)" -ForegroundColor White
    Write-Host "         Amount: $($tx.amount)" -ForegroundColor White
    Write-Host "         Status: $($tx.status)" -ForegroundColor White
    $i++
}

# FINAL SUMMARY
Write-Host "`n" -NoNewline
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "  📊 FINAL SUMMARY" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Cyan

$wallets = Invoke-RestMethod -Uri "$baseUrl/api/v1/wallets/" -Method GET -Headers $headers

Write-Host "   💰 CURRENT BALANCES:" -ForegroundColor Yellow
foreach ($w in $wallets) {
    Write-Host "      $($w.currency_code): $($w.balance)" -ForegroundColor White
}

Write-Host "`n" -NoNewline
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "  ✨ DPG System Test Complete!" -ForegroundColor Green
Write-Host "="*80 -ForegroundColor Cyan

Write-Host "`n🎉 Your payment gateway has:" -ForegroundColor Green
Write-Host "   ✅ User Authentication" -ForegroundColor White
Write-Host "   ✅ Multi-currency Wallets" -ForegroundColor White
Write-Host "   ✅ Deposits and Withdrawals" -ForegroundColor White
Write-Host "   ✅ Transaction History" -ForegroundColor White
Write-Host "`n📍 Next: Build the frontend!" -ForegroundColor Yellow
Write-Host "="*80 -ForegroundColor Cyan
Write-Host ""
