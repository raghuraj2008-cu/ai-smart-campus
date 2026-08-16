$projectDir = "C:\Users\RAGHURAJ P SINGH\ai-smart-campus"
$backupDir = "$projectDir\backups"
$retentionDays = 7

if (!(Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

$date = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupFile = "$backupDir\smart_campus_$date.sql"

Set-Location $projectDir
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres smart_campus | Out-File -FilePath $backupFile -Encoding utf8

Write-Host "Backup created: $backupFile"

$limitDate = (Get-Date).AddDays(-$retentionDays)
Get-ChildItem -Path $backupDir -Filter "*.sql" | Where-Object { $_.LastWriteTime -lt $limitDate } | Remove-Item -Force
Write-Host "Cleaned up database dumps older than $retentionDays days."
