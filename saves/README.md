# Saves

这里用于说明 COC 跑团存档。v2 `.cocsave.json` 默认不再写入 skill 安装目录，而是写入 `scripts/memory.py` 的数据目录。

默认存档文件名类似：

```text
<团名>_20260427_213000.cocsave.json
```

这些文件包含完整跑团记忆，包括 Keeper Only 信息、暗骰、隐藏 SAN 和未公开真相。为了避免剧透，玩家不应直接打开存档内容阅读。

每个 v2 存档都会内置结构化记忆：

- 玩家可知续跑摘要：用于给玩家做“上回回顾”。
- Keeper 续跑摘要：用于模型/Keeper 恢复幕后真相、线索网络、NPC 状态、暗骰、威胁时钟和未结算事项。
- 当前状态快照：调查员、NPC、地点、物品、线索、线程和时钟。

生成快照：

```bash
python scripts/memory.py snapshot --name "<团名>"
```

需要在另一台电脑继续游玩时，只复制对应存档文件，然后在目标电脑运行：

```bash
python scripts/memory.py load --file "<存档名>.cocsave.json"
python scripts/memory.py recall --name "<团名>" --keeper
```
