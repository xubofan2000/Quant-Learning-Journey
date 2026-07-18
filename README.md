# Bohr：就业导向的量化学习工程

Bohr 服务于“一年内获得量化相关岗位”的现实目标，以全职工作并行、稳定产出和可验证能力为约束。建议长期投入 12-15 小时/周，不建议裸辞；进度以能力验收为主，不再以连续打卡或 `20/28 Days` 代表掌握。

第一求职目标依次是：量化数据开发 / 金融数据工程、量化研究平台 Python 开发、投研数据支持 / 金融数据分析 / 风险数据岗位。中低频量化开发与量化研究助理是第二阶段目标；高频研究、低延迟 C++ 和高学历门槛的纯策略研究不是一年内主线。学历、专业、所在城市和可接受城市仍待学习者确认。

## 从这里开始

1. 查看当前能力矩阵：`curriculum/plans/JOB_CAPABILITY_MATRIX.md`。
2. 从 `curriculum/plans/NEXT_12_WEEKS.md` 的 Week 1 开始；第一项任务是不看原代码完成最新 Week 3 恢复训练。
3. 运行历史证据和课程一致性审计：
   ```powershell
   .\.venv\Scripts\python.exe project\scripts\project_audit.py
   .\.venv\Scripts\python.exe project\scripts\curriculum_audit.py
   ```
4. 每周复制 `project/templates/WEEKLY_ACCEPTANCE_TEMPLATE.md`，记录独立实现、自动测试、口述验收和补救。
5. 提交前运行测试：
   ```powershell
   .\.venv\Scripts\python.exe -m unittest discover -s project\tests -v
   ```

## 快速导航

| 你想做什么                 | 去哪里                             |
| -------------------------- | ---------------------------------- |
| 看未来 12 周任务           | `curriculum/plans/NEXT_12_WEEKS.md` |
| 查看当前能力状态           | `curriculum/plans/JOB_CAPABILITY_MATRIX.md` |
| 编写/阅读学习代码与笔记    | `Learning_Vault/`                |
| 使用本地数据               | `Database/`                      |
| 查长期路线和资料索引       | `curriculum/knowledge-base/`     |
| 使用脚本、模板、规范与测试 | `project/`                       |

完整结构、各目录职责和常用命令见 `project/docs/STRUCTURE_GUIDE.md`。

## 进度与证据原则

- `curriculum/plans/` 定义任务与退出门槛；岗位能力矩阵记录经过验收的能力；`Learning_Log.md` 和 `Learning_Vault/` 保存历史过程与证据。
- 文件存在、AI 生成代码、历史打卡、最高收益或 GitHub 星数都不是掌握或项目质量的充分证据。
- 同一能力只有在“能不看答案独立实现 + 测试通过 + 能解释金融含义和假设”同时成立时才标记为掌握。
- `R @ W.T` 是固定权重收益的向量化演示，不是包含交易、成本、现金和无法成交的完整回测。
- p-value 只能量化特定假设与模型前提下的统计证据；Monte Carlo/GBM 用于情景模拟、风险分析和模型理解；PCA 的 PC1 不能仅凭模拟数据命名为市场 Beta。
- 研究结论遵守 `project/docs/RESEARCH_PROTOCOL.md`。Agent 最多 2-3 周且有前置门槛；模拟执行与治理最多 4-6 周；真实交易不属于当前课程默认范围。
