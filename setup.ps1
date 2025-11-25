# Gamma Clone - Quick Setup Script
# Run this in PowerShell to set up the complete project

Write-Host "================================" -ForegroundColor Cyan
Write-Host "🎨 GAMMA CLONE - SETUP SCRIPT" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Docker
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✓ $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found. Install Docker Desktop for easier setup" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "SETUP OPTIONS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Docker Setup (Recommended)" -ForegroundColor Green
Write-Host "   - Easiest setup with all services"
Write-Host "   - PostgreSQL, Redis, MongoDB included"
Write-Host ""
Write-Host "2. Local Development Setup" -ForegroundColor Yellow
Write-Host "   - Manual setup, more control"
Write-Host "   - Requires PostgreSQL, Redis installed"
Write-Host ""

$choice = Read-Host "Choose setup method (1 or 2)"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "DOCKER SETUP" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check if .env exists
    if (!(Test-Path ".env")) {
        Write-Host "Creating .env file..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env file" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY" -ForegroundColor Yellow
        Write-Host ""
        $openaiKey = Read-Host "Enter your OpenAI API key (or press Enter to edit .env later)"
        
        if ($openaiKey) {
            (Get-Content ".env") -replace "OPENAI_API_KEY=sk-your-key-here", "OPENAI_API_KEY=$openaiKey" | Set-Content ".env"
            Write-Host "✓ API key configured" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "Starting Docker containers..." -ForegroundColor Yellow
    docker-compose up -d
    
    Write-Host ""
    Write-Host "Waiting for services to be healthy..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    Write-Host ""
    Write-Host "✅ SETUP COMPLETE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Services running:" -ForegroundColor Cyan
    Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  - PostgreSQL: localhost:5432" -ForegroundColor White
    Write-Host "  - Redis: localhost:6379" -ForegroundColor White
    Write-Host "  - MongoDB: localhost:27017" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Test API: Invoke-WebRequest http://localhost:8000/health" -ForegroundColor White
    Write-Host "  2. Generate themes: docker-compose exec backend python scripts/seed_themes.py" -ForegroundColor White
    Write-Host "  3. View logs: docker-compose logs -f backend" -ForegroundColor White
    Write-Host ""
    
} elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host "LOCAL DEVELOPMENT SETUP" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Create virtual environment
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    Set-Location backend
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
    
    # Activate virtual environment
    Write-Host ""
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
    
    # Install dependencies
    Write-Host ""
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    Write-Host "(This may take a few minutes)" -ForegroundColor Gray
    pip install -r requirements.txt
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
    
    # Create .env
    Set-Location ..
    if (!(Test-Path ".env")) {
        Write-Host ""
        Write-Host "Creating .env file..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env file" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "✅ SETUP COMPLETE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Before starting the server:" -ForegroundColor Yellow
    Write-Host "  1. Edit .env and add your OPENAI_API_KEY" -ForegroundColor White
    Write-Host "  2. Ensure PostgreSQL is running on localhost:5432" -ForegroundColor White
    Write-Host "  3. Create database: createdb gamma_clone" -ForegroundColor White
    Write-Host "  4. Run schema: psql gamma_clone < backend/db/schema.sql" -ForegroundColor White
    Write-Host "  5. Ensure Redis is running on localhost:6379" -ForegroundColor White
    Write-Host ""
    Write-Host "To start the server:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor White
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "  python main.py" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "Invalid choice. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host "================================" -ForegroundColor Cyan
Write-Host "📚 DOCUMENTATION" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Complete documentation: README.md" -ForegroundColor White
Write-Host "API documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
Write-Host ""
