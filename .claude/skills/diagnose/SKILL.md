# 环境诊断

当调用此技能时，按以下步骤自动检测环境和常见问题：

1. 运行 `uname -a` 和 `pwd` **确认当前环境**（WSL / Git Bash / MINGW64 / 原生 Linux / PowerShell）
2. 检查 Node.js 版本和 npm/pnpm 可用性
3. 检查 Python 版本和 pip/uv 可用性
4. 测试 MCP 服务器连接状态
5. 检查常见问题：代理设置、PATH 配置、锁文件冲突
6. **以清晰的表格格式报告发现**

**不要假设环境——永远先验证。**
