# Saves

这里用于保存玩家主动导出的 COC 跑团存档。

默认存档文件名类似：

```text
<团名>_20260427_213000.cocsave.json
```

这些文件包含完整跑团记忆，包括 Keeper Only 信息、暗骰、隐藏 SAN 和未公开真相。为了避免剧透，玩家不应直接打开存档内容阅读。

每个存档都会内置两份续跑摘要：

- 玩家可知续跑摘要：用于给玩家做“上回回顾”。
- Keeper 续跑摘要：用于模型/Keeper 在另一台电脑上恢复幕后真相、剧本当前节点、线索网络、NPC 剧本功能、暗骰、倒计时和未结算事项。

生成的 `.cocsave.json` 文件默认不会提交到 Git。需要在另一台电脑继续游玩时，只复制对应存档文件，然后在目标电脑运行：

```bash
python scripts/memory.py load --file saves/<存档名>.cocsave.json
python scripts/memory.py recall --name "<团名>" --keeper
```
