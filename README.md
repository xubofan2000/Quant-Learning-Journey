# Bohr：AI 辅助量化学习项目

Bohr 是一套以真实代码、研究规范和复盘产物为核心的量化学习工程。根目录只保留学习入口、学习产物和数据；课程资料与项目工具已按用途收纳。

## 从这里开始

1. 运行当前状态审计：
   ```powershell
   .\.venv\Scripts\python.exe project\scripts\project_audit.py
   ```
2. 根据输出定位当天任务：`curriculum/plans/TODO_Phase1.md`。
3. 在对应的 `Learning_Vault/Phase1_Month1/WeekN/` 编写、运行和理解代码。
4. 完成学习检验与总结后，更新 `Learning_Log.md` 和 TODO。
5. 运行进度条更新脚本刷新状态：
   ```powershell
   .\.venv\Scripts\python.exe project\scripts\update_progress.py
   ```
6. 提交前运行测试并使用 Git 提交代码：
   ```powershell
   .\.venv\Scripts\python.exe -m unittest discover -s project\tests -v
   ```

## 快速导航

| 你想做什么 | 去哪里 |
| --- | --- |
| 看今天该学什么 | `curriculum/plans/` |
| 查看当前学习状态 | `Learning_Log.md` 或状态审计命令 |
| 编写/阅读学习代码与笔记 | `Learning_Vault/` |
| 使用本地数据 | `Database/` |
| 查长期路线和资料索引 | `curriculum/knowledge-base/` |
| 使用脚本、模板、规范与测试 | `project/` |

完整结构、各目录职责和常用命令见 `project/docs/STRUCTURE_GUIDE.md`。

## 基本原则

- `curriculum/plans/` 定义任务范围，`Learning_Log.md` 记录学习者确认的完成状态，`Learning_Vault/` 保存证据。
- 代码文件存在不等于已完成学习；以审计结果和学习者确认推进进度。
- 研究结论须遵守 `project/docs/RESEARCH_PROTOCOL.md`，真实交易相关内容默认只在模拟环境中开展。
