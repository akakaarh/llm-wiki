# LLM Wiki — 父级协调层

这是多知识库的协调入口。

## Vaults

- `embedded/` — 嵌入式知识库 Vault
- `software/` — 软件知识库 Vault（已激活，正在进行 Linux 存储 I/O 学习）

## 当前工作 Vault

无偏好。用户在对话中指定。

## 通用原则

1. Wiki 是知识的持久化积累，不是每次问答从头推导
2. Raw sources 不可修改
3. LLM 负责所有 wiki 页面的创建、维护、交叉引用
4. 好的 Query 答案应存回 wiki
5. 定期 Lint 保持 wiki 健康

详见各 Vault 的 CLAUDE.md
