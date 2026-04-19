# 我的第一个 Agent

基于 Ollama 本地大模型的 AI 智能体，支持工具调用。

## 功能

- 本地 LLM 连接（Ollama）
- 工具注册与调用
- 支持自定义 Tool 扩展

## 依赖

```bash
pip install requests
```

## 运行

```bash
python agent.py
```

## 工具调用格式

```
ACTION: tool_name | param1=value1
```

## 内置工具

| 工具名 | 说明 |
|--------|------|
| search | 搜索网络 |
| calculate | 计算数学表达式 |