# Bohr 项目治理规则

## 目的

让学习进度可追踪、学习成果可验证、计划变更可回溯；避免 README 快照、待提交文件与打卡记录彼此漂移。

## 三类事实源

| 维度 | 权威位置 | 更新时机 | 不承担的职责 |
| --- | --- | --- | --- |
| 学习范围与验收 | `curriculum/plans/` | 变更任务前 | 不声明学习已完成 |
| 学习者确认的完成状态 | `Learning_Log.md` | 代码运行、检验与总结均确认后 | 不替代任务定义 |
| 代码、检验和总结证据 | `Learning_Vault/` | 学习过程 | 文件存在不等于已掌握 |

根目录的 `README.md` 只说明项目定位和入口，不记录会过时的完成天数。

## 日常闭环

1. 从 `curriculum/plans/` 读取当天任务、输入、输出与验收条件。
2. 在 `Learning_Vault/` 创建代码；代码必须可独立运行或说明数据前置条件。
3. 完成学习检验和总结；记录不确定点与复习日期。
4. 学习者确认运行结果和理解程度后，再同时更新 TODO 与 `Learning_Log.md`。
5. 运行 `python project/scripts/project_audit.py`；仅当审计无意外偏差时提交 Git。

## 偏差处理

| 情况 | 处理方式 |
| --- | --- |
| 有代码但未打卡 | 标为“待学习者确认”，不自动勾选 TODO 或日志 |
| 日志完成但没有代码 | 暂停推进，补回产物或记录其替代证据 |
| TODO 与日志不同 | 明确记录变更原因；先更新计划，再更新日志 |
| 新增计划外练习 | 放入 `Practice1/` 或对应练习目录，不作为正式完成证据 |

## 自动审计

```powershell
python project/scripts/project_audit.py
python project/scripts/project_audit.py --write-report
```

脚本只读取三个事实源，并把派生报告写到被 Git 忽略的 `project/reports/PROJECT_STATUS.md`；它绝不修改学习进度。

## Agent Skill 维护

仓库已追踪的 `.agent/skills/` 是版本控制中的技能源。`.agents/` 与 `.claude/` 是本地客户端副本；在修改工作流时，应先选择一个源文件更新并显式同步，不能假设多个副本天然一致。
