# OpenCode 本机接入维护

此目录保存 Antigravity Tools 接入本机 OpenCode 的维护脚本，与教学竞赛课程无关。

- `sync_antigravity.py`：读取本机代理模型目录，仅更新 OpenCode 的 Antigravity 提供商；默认只预览，`--apply` 才写入。
- 不保存或输出实际密钥，不修改 Antigravity Tools 的账号和代理设置。
- 写入前备份原文件；保留其他提供商、默认模型和 MCP 配置。
- 临时验证文件位于上级 `.tmp/opencode-antigravity/`，交付不依赖这些文件。
