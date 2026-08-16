Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Starting Smart Campus Zero-Downtime Deploy" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Pull latest code from GitHub
Write-Host "`n[1/5] Pulling latest changes from main branch..." -ForegroundColor Yellow
git pull origin main

# 2. Build updated images
Write-Host "`n[2/5] Building updated container images..." -ForegroundColor Yellow
docker compose -f docker-compose.prod.yml build api frontend

# 3. Apply rolling container updates
Write-Host "`n[3/5] Launching updated services..." -ForegroundColor Yellow
docker compose -f docker-compose.prod.yml up -d --remove-orphans

# 4. Clean up dangling images
Write-Host "`n[4/5] Pruning obsolete Docker resources..." -ForegroundColor Yellow
docker image prune -f

# 5. Active Health Check Polling
Write-Host "`n[5/5] Waiting for Gateway and API readiness..." -ForegroundColor Yellow
$retries = 10
$ready = $false

while ($retries -gt 0) {
    try {
        $res = Invoke-WebRequest -Uri "http://localhost/" -Method Get -TimeoutSec 3 -UseBasicParsing
        if ($res.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        # Retry until upstream opens
    }
    Start-Sleep -Seconds 2
    $retries--
}

if ($ready) {
    Write-Host "Deployment Successful! Stack is active and healthy." -ForegroundColor Green
} else {
    Write-Host "Warning: Stack took longer than expected to respond." -ForegroundColor Yellow
}

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host " Stack Status Summary:" -ForegroundColor Cyan
docker compose -f docker-compose.prod.yml ps
