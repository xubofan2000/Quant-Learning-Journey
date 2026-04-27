# 项目结构详细地图

> 本文件供 agent 在需要更详细结构信息时按需读取，SKILL.md 已包含核心摘要。

## 完整目录树

```
d:\project\Bohr\
│
├── .agent\
│   └── skills\
│       ├── notebooklm-mcp\         # NotebookLM 操作 skill
│       │   └── SKILL.md
│       └── quant-learning-workflow\ # 本 skill（当前文件所在位置）
│           ├── SKILL.md
│           ├── scripts\
│           │   └── detect_progress.py
│           └── resources\
│               ├── project-map.md   # 本文件
│               ├── code-template.md
│               └── summary-template.md
│
├── AI_Quant_Knowledge_Base\         # Phase 目标文档（4个阶段）
│   ├── 01_Phase1_基建与数理.md       # Python/Pandas/NumPy/线性代数
│   ├── 02_Phase2_框架与因子.md       # VectorBT/Alphalens/FinGPT
│   ├── 03_Phase3_Agent架构.md       # LangGraph/MCP
│   ├── 04_Phase4_合规与实盘.md       # MiniQMT/监管
│   └── 量化学习资料索引.md            # 295条学习资源，分阶段分类
│
├── plans\
│   └── TODO_Phase1.md              # Phase1 Month1 逐日任务（28天）
│                                   # 格式: - [ ] 任务: ... / - [ ] 产出: ...
│
├── Learning_Vault\
│   └── Phase1_Month1\
│       ├── Week1\                  # SQL→Pandas 思维映射（已完成）
│       │   ├── day1_duckdb_init.py
│       │   ├── Day1_DuckDB基建总结.md
│       │   ├── ... (day2-7, Day2-7 总结)
│       │   ├── Week1_Flashcards.md
│       │   └── Week1_Summary.md
│       │
│       ├── Week2\                  # 金融时序预处理（已完成）
│       │   ├── day1_data_cleaning.py
│       │   ├── Day1_时序索引与缺失值填充总结.md
│       │   ├── ... (day2-7, Day2-7 总结)
│       │   └── Week2_综合总结.md
│       │
│       ├── Week3\                  # 线性代数与资产组合（进行中）
│       │   ├── day1_vector_dot_product.py      ✅
│       │   ├── Day1_向量点乘与组合收益率总结.md  ✅
│       │   ├── day2_elementwise_vs_matmul.py   ✅
│       │   ├── Day2_逐元素乘法与矩阵乘法总结.md  ✅
│       │   ├── day3_covariance_matrix.py       ✅
│       │   ├── Day3_协方差矩阵总结.md            ✅
│       │   ├── day4_portfolio_variance.py      ✅
│       │   ├── Day4_组合方差总结.md              ✅
│       │   ├── Day4_矩阵推导与多项式展开专项总结.md ✅ (额外补充笔记)
│       │   ├── day5_markowitz_optimizer.py     ⚠️ 与TODO计划不符（见下方说明）
│       │   └── Day5_马科维茨优化求解总结.md      ⚠️ 与TODO计划不符
│       │
│       ├── Week4\                  # 概率统计与风险分布（未开始）
│       └── Practice1\             # 练习草稿（非正式）
│           ├── test.py
│           ├── testw3d2.py
│           └── ...
│
├── Database\
│   └── files\
│       ├── panel_50stocks.parquet  # 50只股票面板数据（Week3+核心数据源）
│       └── ...
│
├── Learning_Log.md                 # ⭐ 核心打卡文件
│   # 结构: 每个 Week 一个 <details> 折叠块
│   # 表头: | 打卡 | 复习回溯(1/3/7) | Day | 产出成果定位 | 今日高光摘要 |
│
├── update_progress.py             # 读取 Learning_Log.md，自动更新进度条数字
│
└── .gitignore                     # 排除: .venv/, Database/files/, notebooklm_cache/
```

## ⚠️ 已知计划偏差记录

**Week3 Day5 偏差**：
- **TODO 计划**：特征值/特征向量 + PCA + `scipy.linalg.eigh` 解剖协方差矩阵
- **实际文件**：`day5_markowitz_optimizer.py` → scipy.optimize SLSQP 马科维茨优化（应为 Week 后续内容）
- **处理原则**：以 TODO 为准。Day5 实际应学特征值/PCA，现有文件内容可归入 Day6 或调整计划

## Learning_Log.md 格式参考

```markdown
### 📊 当前阶段进度: Phase 1 (19/28 Days)
进度条: [===================.........] 67%

<details open>
<summary><b>🔥 Week 3 / ...</b></summary>

| 打卡 | 复习回溯 (1/3/7) | Day | 产出成果定位 | 今日高光摘要 |
| ---- | ---------------- | --- | ------------ | ------------ |
| [x]  | [ ]              | **Day 1** | D:\...\day1_xxx.py | 高光内容 |
| [ ]  | [ ]              | **Day 5** | `Learning_Vault/.../Week3/` | [待填写] |

</details>
```

## TODO_Phase1.md 格式参考

```markdown
## Week 3: ...
### Day 5
- [ ] 任务：特征值与特征向量的金融具象意义...
- [ ] 产出：通过 `scipy.linalg.eigh` 解剖你生成的协方差矩阵...
```

## NotebookLM 知识库

- **URL**: https://notebooklm.google.com/notebook/64bd973b-9779-4be9-89e7-e0349250c385
- **名称**: 个人量化入行知识库（AI驱动量化转型知识库）
- **内容**: 约 295 条来源，涵盖 Phase1-3 的全部学习资源
- **调用方式**: 使用 `notebooklm-mcp` skill 中的 `notebook_query` 工具
