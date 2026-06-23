# Scenarios

这里用于保存生成的 COC 模组、场景大纲或 Keeper 笔记。v2 长期跑团记忆默认不再写入 skill 安装目录。

示例文件名：

```text
scenarios/榕渊_福州现代CoC模组.md
scenarios/miskatonic_museum_outline.md
scenarios/榕渊_备团笔记.md
```

默认提交本说明文件以保留目录结构；实际生成的模组和笔记会被 `.gitignore` 忽略，避免误提交未公开内容、暗骰结果或剧透信息。

长期跑团建议用 `scripts/memory.py` 创建和更新 v2 记忆。默认数据目录：

- macOS/Linux: `~/.codex/data/coc-trpg-skill`
- Windows: `%APPDATA%\coc-trpg-skill`

如果旧版本已经在这里生成 `*_memory.json` 或 `*_memory.md`，可先归档：

```bash
python scripts/memory.py archive-legacy
```

如果需要把进度复制到另一台电脑，优先使用：

```bash
python scripts/memory.py snapshot --name "<团名>"
```

它会在 v2 数据目录的 `saves/` 下导出单个 `.cocsave.json` 存档文件。
