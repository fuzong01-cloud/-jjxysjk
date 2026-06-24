# 开发指南

使用 Python 3.12、类型标注和 snake_case。模型变更后运行 `alembic revision --autogenerate` 并审阅迁移；导入映射、接口模式、页面和测试需要同步更新。所有写操作必须进入审计日志，敏感数据必须脱敏。提交前运行 `scripts/test.ps1`。项目专项工作流见 `.agents/skills`。

