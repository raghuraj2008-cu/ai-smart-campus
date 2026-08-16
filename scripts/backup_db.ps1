$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = ".\backups\smart_campus_db_$timestamp.sql"

Write-Host "Creating PostgreSQL backup at $backupFile..." -ForegroundColor Cyan
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres smart_campus > $backupFile

if (Test-Path $backupFile) {
    $size = (Get-Item $backupFile).Length / 1KB
    Write-Host "Backup completed successfully! ($([Math]::Round($size, 2)) KB)" -ForegroundColor Green
} else {
    Write-Host "Backup failed!" -ForegroundColor Red
}
