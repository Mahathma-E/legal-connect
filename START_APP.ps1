# LegalConnect - Quick Start Script
# Run this to start both backend and frontend

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "  LegalConnect - Starting Application" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan

# Check if backend is already running
$backendRunning = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*legal-connect*"}

if ($backendRunning) {
    Write-Host "`n✅ Backend already running (PID: $($backendRunning.Id))" -ForegroundColor Green
} else {
    Write-Host "`n🚀 Starting Backend Server..." -ForegroundColor Yellow
    Write-Host "   Location: d:\Project Law\legal-connect\backend" -ForegroundColor Gray
    
    # Start backend in new window
    Start-Process powershell -ArgumentList @"
        -NoExit
        -Command
        cd 'd:\Project Law\legal-connect';
        .\.venv\Scripts\Activate.ps1;
        cd backend;
        Write-Host '🔧 Backend Server Starting...' -ForegroundColor Cyan;
        python app.py
"@
    
    Write-Host "   ✅ Backend server starting in new window..." -ForegroundColor Green
    Start-Sleep -Seconds 3
}

# Check if frontend is already running
$frontendRunning = Get-Process node -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*legal-connect*"}

if ($frontendRunning) {
    Write-Host "`n✅ Frontend already running (PID: $($frontendRunning.Id))" -ForegroundColor Green
} else {
    Write-Host "`n🎨 Starting Frontend Server..." -ForegroundColor Yellow
    Write-Host "   Location: d:\Project Law\legal-connect\frontend" -ForegroundColor Gray
    
    # Start frontend in new window
    Start-Process powershell -ArgumentList @"
        -NoExit
        -Command
        cd 'd:\Project Law\legal-connect\frontend';
        Write-Host '🎨 Frontend Server Starting...' -ForegroundColor Cyan;
        npm start
"@
    
    Write-Host "   ✅ Frontend server starting in new window..." -ForegroundColor Green
    Start-Sleep -Seconds 2
}

Write-Host "`n" -NoNewline
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "  🎉 LegalConnect Started Successfully!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host "`n📍 Access Points:" -ForegroundColor Yellow
Write-Host "   Frontend: " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend:  " -NoNewline -ForegroundColor Gray
Write-Host "http://localhost:5000" -ForegroundColor Cyan

Write-Host "`n👤 Demo Accounts:" -ForegroundColor Yellow
Write-Host "   Public User:" -ForegroundColor Gray
Write-Host "     Email:    john.public@demo.com" -ForegroundColor White
Write-Host "     Password: demo123" -ForegroundColor White
Write-Host "`n   Advocate User:" -ForegroundColor Gray
Write-Host "     Email:    sarah.advocate@demo.com" -ForegroundColor White
Write-Host "     Password: demo123" -ForegroundColor White

Write-Host "`n🎯 Quick Test:" -ForegroundColor Yellow
Write-Host "   1. Open: http://localhost:3000" -ForegroundColor White
Write-Host "   2. Login as john.public@demo.com" -ForegroundColor White
Write-Host "   3. Search for 'Sarah' in the search bar" -ForegroundColor White
Write-Host "   4. Click on Sarah Advocate's profile" -ForegroundColor White
Write-Host "   5. See the [📞 Call] button!" -ForegroundColor White

Write-Host "`n" -NoNewline
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "  Press Ctrl+C to stop this script" -ForegroundColor Gray
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host "`nWaiting for servers to fully start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`n✅ Servers should be ready now!" -ForegroundColor Green
Write-Host "   Check the new terminal windows for server logs.`n" -ForegroundColor Gray

# Keep script running
Read-Host "Press Enter to exit"
