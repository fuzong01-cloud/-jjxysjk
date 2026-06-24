$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
New-Item -ItemType Directory -Path backups -Force | Out-Null
Copy-Item -LiteralPath data\touyan.db -Destination "backups\manual_$stamp.db"
Write-Host "备份已创建：backups\manual_$stamp.db"

