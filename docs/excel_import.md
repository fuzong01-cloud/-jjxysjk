# Excel 导入指南

支持 `.xlsx`，必填“学员姓名”和“身份证号”。网页端在“数据导入”完成上传预览和确认写入；命令行可使用：

```powershell
.\.venv\Scripts\python.exe scripts\import_excel.py --file "..\头雁学员名单2024_学员名单_原版.xlsx" --dry-run
```

重复身份证号按确认结果更新；荣誉、年度营收和产业序号组拆成明细。错误行保留原始行号，未知列作为警告。详细规则见 [系统指南](system_guide.md#excel-导入)。

