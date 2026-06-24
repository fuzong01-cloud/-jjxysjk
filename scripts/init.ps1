$ErrorActionPreference = 'Stop'
if (-not (Test-Path '.venv')) { py -3.12 -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
if (-not (Test-Path '.env')) { Copy-Item .env.example .env }
& .\.venv\Scripts\python.exe -m alembic upgrade head
Write-Host '初始化完成。请修改 .env 中的管理员密码，然后运行 scripts\start.ps1。'
