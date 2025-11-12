# DPG Backend Startup Script (Development Mode with Auto-Reload)
# Use this when actively developing and need instant updates

Write-Host "🔄 Starting DPG Backend (Development Mode - Auto-Reload Enabled)" -ForegroundColor Yellow
Write-Host ""
Write-Host "This mode provides:" -ForegroundColor Cyan
Write-Host "  ✅ Automatic code reload on file changes" -ForegroundColor Green
Write-Host "  ⚠️  Server restarts may log users out" -ForegroundColor Yellow
Write-Host "  ⚠️  Use for active development only" -ForegroundColor Yellow
Write-Host ""
Write-Host "For stable sessions, use start_stable.ps1 instead" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server starting on http://localhost:9000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:9000/docs" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
& "$PSScriptRoot\..\venv_new\Scripts\Activate.ps1"

# Set environment to development mode (enables auto-reload)
$env:NODE_ENV = "development"

# Start server
cd "$PSScriptRoot"
python main.py
