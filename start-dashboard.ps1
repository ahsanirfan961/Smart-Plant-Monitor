# Start the dashboard server locally
Write-Host "Starting Smart Plant IoT Dashboard Server..." -ForegroundColor Green
Write-Host "Changing to dashboard directory..." -ForegroundColor Cyan

cd dashboard/backend-api

Write-Host "Installing dependencies..." -ForegroundColor Cyan
npm install

Write-Host "Starting server on http://localhost:3003" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
npm start
