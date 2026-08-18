param (
    [Parameter(Mandatory=$false)]
    [string]$BackupFile
)

if (-not $BackupFile) {
    $latestBackup = Get-ChildItem -Path .\backups\smart_campus_db_*.sql | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $latestBackup) {
        Write-Host "No backup files found in .\backups\" -ForegroundColor Red
        exit 1
    }
    $BackupFile = $latestBackup.FullName
}

if (-not (Test-Path $BackupFile)) {
    Write-Host "Target backup file does not exist: $BackupFile" -ForegroundColor Red
    exit 1
}

Write-Host "Restoring PostgreSQL database from: $BackupFile..." -ForegroundColor Cyan

# Terminate existing connections, drop and recreate schema, then restore snapshot
docker compose -f docker-compose.prod.yml exec -T db psql -U postgres -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'smart_campus' AND pid <> pg_backend_pid();"
docker compose -f docker-compose.prod.yml exec -T db psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS smart_campus;"
docker compose -f docker-compose.prod.yml exec -T db psql -U postgres -d postgres -c "CREATE DATABASE smart_campus;"

Get-Content $BackupFile | docker compose -f docker-compose.prod.yml exec -T db psql -U postgres -d smart_campus

Write-Host "Database successfully restored from $BackupFile!" -ForegroundColor Green
