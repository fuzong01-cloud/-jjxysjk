# Windows 部署指南

```powershell
.\scripts\init.ps1
notepad .env
.\scripts\start.ps1
```

必须修改 `.env` 中的默认密码和密钥。系统默认只监听 `127.0.0.1:8000`。局域网部署应增加 HTTPS 反向代理、收紧目录权限并启用安全 Cookie。升级前备份，再执行 `python -m alembic upgrade head`。详见 [系统指南](system_guide.md#部署与升级)。

