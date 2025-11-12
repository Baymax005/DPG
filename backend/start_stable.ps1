# DPG Backend Startup Script (No Auto-Reload)
# Use this for stable development sessions without constant server restarts

Write-Host "🚀 Starting DPG Backend (Stable Mode - No Auto-Reload)" -ForegroundColor Green
Write-Host ""
Write-Host "This mode provides:" -ForegroundColor Cyan
Write-Host "  ✅ Stable server sessions" -ForegroundColor Green
Write-Host "  ✅ No automatic logouts" -ForegroundColor Green
Write-Host "  ✅ 24-hour token expiration" -ForegroundColor Green
Write-Host "  ⚠️  Manual restart needed for code changes" -ForegroundColor Yellow
Write-Host ""
Write-Host "To restart server after code changes, press Ctrl+C and run this script again" -ForegroundColor Yellow
Write-Host ""
Write-Host "Server starting on http://localhost:9000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:9000/docs" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
& "$PSScriptRoot\..\venv_new\Scripts\Activate.ps1"

# Set environment to production mode (disables auto-reload)
$env:NODE_ENV = "production"

# Start server
cd "$PSScriptRoot"
python main.py
