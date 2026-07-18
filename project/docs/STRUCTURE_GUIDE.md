# Bohr 项目结构指南

## 进入项目后怎么做

```text
打开 README.md
    ↓
查看 JOB_CAPABILITY_MATRIX.md 与 NEXT_12_WEEKS.md
    ↓
运行 project_audit.py 与 curriculum_audit.py
    ↓
完成本周独立实现、测试、报告和口述
    ↓
只有三项门槛都通过才更新能力矩阵
```

## 当前目录树

```text
Bohr/
├── README.md                         # 唯一学习入口：先看这里
├── Learning_Log.md                   # 历史打卡与学习证据索引（非能力主状态）
├── Bohr.code-workspace               # VS Code 工作区
│
├── Learning_Vault/                   # 每日代码、学习检验、总结、复习包
│   ├── Phase1_Month1/
│   └── Reviews/
├── Database/                         # 本地原始/处理后金融数据（默认不提交）
│   └── files/
│
├── curriculum/                       # “学什么”
│   ├── plans/                        # 12 周计划、能力矩阵、历史 TODO 与阶段计划
│   └── knowledge-base/               # 课程知识索引、阶段边界与资料入口
│
├── project/                          # “如何把项目维护好”
│   ├── docs/                         # 治理、路线图、研究协议、工程规范、本文档
│   ├── scripts/                      # 历史证据审计与课程一致性检查
│   ├── templates/                    # 研究卡与周验收模板
│   ├── tests/                        # 项目工具的自动化测试
│   ├── requirements/                 # 可复现环境的依赖清单
│   └── reports/                      # 本地派生审计报告（Git 忽略）
│
├── notebooklm_cache/                 # NotebookLM 本地缓存；通常无需手动进入
├── .agent/ .agents/ .claude/         # 各客户端的 Agent/Skill 配置
├── .github/                          # CI 检查
├── .vscode/                          # 编辑器配置
└── .gitignore
```

## 目录职责与操作边界

| 目录/文件 | 何时使用 | 不要做什么 |
| --- | --- | --- |
| `README.md` | 每次开始学习 | 不把进度快照写回这里 |
| `curriculum/plans/NEXT_12_WEEKS.md` | 确认本周任务和验收条件 | 不因日历到期自动通过 |
| `curriculum/plans/JOB_CAPABILITY_MATRIX.md` | 记录经验证能力 | 不因文件存在或 AI 生成而升级 |
| `Learning_Log.md` | 查阅历史打卡和摘要 | 不再作为掌握状态事实源 |
| `Learning_Vault/` | 编写学习代码、检验、总结 | 不把正式产物散落到根目录 |
| `Database/` | 读取或生成数据 | 不提交大数据或密钥 |
| `project/` | 调用工具、阅读规范、运行测试 | 不将每日学习脚本放在这里 |
| `.agent/`、`.agents/`、`.claude/` | 维护客户端工作流 | 不在不知道来源的情况下只改其中一个副本 |

## 常用命令

```powershell
# 查看当前学习状态（不会修改文件）
.\.venv\Scripts\python.exe project\scripts\project_audit.py

# 检查 12 周计划、能力矩阵和模板的一致性
.\.venv\Scripts\python.exe project\scripts\curriculum_audit.py

# 生成本地审计报告（写入 project/reports/，不提交 Git）
.\.venv\Scripts\python.exe project\scripts\project_audit.py --write-report

# 验证项目工具和课程契约；Week 3 后还必须包含量化核心测试
.\.venv\Scripts\python.exe -m unittest discover -s project\tests -v
```

## 新文件放置规则

- 新的逐日学习代码、检验和总结：`Learning_Vault/PhaseX_MonthY/WeekN/`。
- 临时探索或复现实验：对应 `Practice` 目录；成熟后再升级为正式研究。
- 正式研究卡、配置与报告：从 Phase 2 起在 `experiments/` 下按研究主题建目录。
- 课程计划、环境扫描：`curriculum/plans/`。
- 项目工具、模板和自动化测试：`project/` 对应子目录。
- 每周验收记录：建议放在相应 `Learning_Vault/Reviews/` 或正式实验目录，链接回能力矩阵。
