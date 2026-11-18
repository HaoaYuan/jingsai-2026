# Antigravity Tools 接入 OpenCode

此脚本将本机 Antigravity Tools 的聊天模型目录同步到 OpenCode 2.x 的 `providers` 配置。密钥仅在运行时从本机配置读取，不包含在脚本中。

预览：

```powershell
python "D:\教学工作知识库\教学竞赛\opencode-integration\sync_antigravity.py"
```

应用：

```powershell
python "D:\教学工作知识库\教学竞赛\opencode-integration\sync_antigravity.py" --apply
```

脚本仅替换 `antigravity-tools` 提供商，保留其他提供商、默认模型及 MCP 设置。写入前在原配置旁生成带时间戳的 `.bak` 备份，写入后重新读取核对。备份与原配置均含本机凭据，不应外发。

执行后重新启动 OpenCode，用 `/models` 选择 Antigravity Tools 模型，或运行：

```powershell
opencode run --model antigravity-tools/gemini-3.8-flash "Reply exactly OK. Do not use tools."
```

模型来自本机 `/v1/models`，不将内部别名和图片生成模型放入编程聊天列表。模型出现在列表中不保证账号实时配额充足。

配置依据：[OpenCode 提供商文档](https://opencode.ai/docs/providers/) 、[OpenCode 配置 Schema](https://opencode.ai/config.json) 。

诊断和验证状态见 [ROADMAP.md](D:/教学工作知识库/教学竞赛/opencode-integration/ROADMAP.md) 。
