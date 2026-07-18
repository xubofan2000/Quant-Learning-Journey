---
name: quant-learning-workflow
description: "管理 Bohr 项目的 AI 量化学习全流程。当用户提到：开始学习、生成代码、生成总结、打卡、制定计划、我学到哪了、今天的课等关键词时触发。"
---

# Bohr 量化学习工作流 (Quant Learning Workflow)

## 2026-07-18 能力验收路由（最高优先级）

本节覆盖下方旧的 28 天、每日打卡和自动生成答案流程；旧流程只为历史兼容保留。

1. 当前计划权威源是 `curriculum/plans/NEXT_12_WEEKS.md`，当前能力权威源是 `curriculum/plans/JOB_CAPABILITY_MATRIX.md`。
2. `Learning_Log.md`、旧 TODO 和 `Learning_Vault/` 是历史记录/证据；文件存在、AI 生成或 `[x]` 不等于掌握。
3. 每次触发先运行只读的 `git status --short --branch`、`project/scripts/project_audit.py` 和 `project/scripts/curriculum_audit.py`，保护未提交修改。
4. 每周使用 `project/templates/WEEKLY_ACCEPTANCE_TEMPLATE.md`。只有学习者“不看答案独立实现 + 自动测试通过 + 能解释金融含义和假设”同时满足，才更新能力矩阵为掌握。
5. 不自动填写恢复训练、面试题或研究练习答案；AI 代码必须由学习者独立复现、测试和口述。
6. 当前具体任务是 `NEXT_12_WEEKS.md` Week 1：不看历史代码完成 `Learning_Vault/Reviews/20260718_Week3_矩阵运算与PortfolioMath/恢复训练_Challenge.py`。未通过内容不得继续标记为掌握。
7. 进度查询输出能力等级、证据、薄弱点、退出门槛和补救措施，不再输出按天进度条作为主要指标。`update_progress.py` 仅报告历史打卡且不写文件。
8. Agent/LLM 最多 2-3 周且需真实因子最终样本外验证；模拟执行/治理 4-6 周；C++、实盘接口和高频研究不进入当前 12 周主线。

若下方任何 Workflow 与本节、研究协议或工程基线冲突，以本节和当前计划为准。

## 项目概览

**项目路径**: `d:\project\Bohr\`
**目标**: 在全职工作并行、12-15 小时/周条件下，一年内获得量化相关岗位
**当前阶段**: 未来 12 周 Week 1 - 恢复训练与真实能力盘点

### 核心目录结构

```
d:\project\Bohr\
├── curriculum/
│   ├── knowledge-base/             # 四个阶段目标与资料索引
│   └── plans/                      # TODO 与 Phase 执行计划
├── Learning_Vault/                 # 学习产出物
│   └── Phase1_Month1/
│       ├── Week1/                  # 每天: dayN_<name>.py + DayN_<中文>总结.md
│       ├── Week2/                  # Week 结束时有 WeekN_综合总结.md
│       ├── Week3/                  # ← 当前 Week
│       ├── Week4/
│       └── Practice1/             # 练习草稿（非正式产出）
├── Database/files/                 # 数据文件（panel_50stocks.parquet等）
├── Learning_Log.md                 # 每日打卡记录（主进度追踪文件）
└── project/scripts/                # 进度审计与进度条更新脚本
```

---

## 目录映射（优先于下方旧目录示例）

项目已完成目录收纳。所有学习工作流必须使用以下路径：

- 学习计划：`curriculum/plans/`
- 阶段目标与资料索引：`curriculum/knowledge-base/`
- 学习代码与总结：`Learning_Vault/`
- 数据：`Database/`
- 进度脚本：`project/scripts/update_progress.py`
- 状态审计：`project/scripts/project_audit.py`
- 完整结构指南：`project/docs/STRUCTURE_GUIDE.md`

下方历史目录树仅供背景参考；如与本节冲突，以本节为准。

## 第一步（必须）：进度检测

**每次触发 skill 后，在做任何事之前，必须先执行进度检测。**

### 检测步骤（按顺序）

1. **读取 `Learning_Log.md`** → 找到第一个 `[ ]`（未打卡）的 Day，确定当前 Week 和 Day 编号
2. **读取 `curriculum/plans/TODO_Phase1.md`** → 找到对应 Day 的任务描述和产出要求（**TODO 是权威来源**）
3. **扫描 `Learning_Vault/.../WeekN/` 目录** → 检查实际文件存在情况

### 三源交叉判断逻辑

| Log 状态 | TODO 状态 | 文件存在 | 结论 |
|---------|---------|---------|------|
| `[ ]` 未打卡 | `[ ]` 未勾选 | .py 不存在 | **今日未开始** → 执行 Workflow A |
| `[ ]` 未打卡 | `[ ]` 未勾选 | .py 存在但无总结 | **代码已生成待确认** → 询问用户进度 |
| `[x]` 已打卡 | `[x]` 已勾选 | .py + .md 均存在 | **已完成** → 进入下一天 |
| 不一致 | 不一致 | 文件与 TODO 描述不符 | **⚠️ 检测到偏差** → 见下方规则 |

### ⚠️ 计划偏差处理规则

如果发现实际代码文件与 TODO 中当天任务描述不符（如发现了计划外的代码文件），必须：

1. **明确告知用户**："检测到 DayN 的实际文件（`actual_filename.py`）与 TODO 计划任务（`计划描述`）不一致，可能是前序对话发生了偏差。"
2. **询问用户如何处理**：以 TODO 计划为准重新生成 / 承认此文件为新计划并更新 TODO
3. **绝不沉默接受偏差**，绝不基于错误文件继续工作
4. **检查版本控制状态**：如果偏差是由于用户临时测试导致的未提交代码，主动询问用户是否需要执行 `git status` 或 `git diff` 来确认改动，或者建议使用 `git restore` 丢弃不需要的测试代码，以保持主分支的纯净。

---

## 工作流定义

### Workflow A：每日学习（主流程，混合模式）

```
[自动] Step 1: 进度检测（见上方规则）
[自动] Step 2: 展示今日任务（从 TODO 读取）
       → 告知用户：今天是 PhaseX/WeekY/DayZ，任务是「...」，产出是「...」

[自动] Step 3: 生成代码文件
       → 路径: Learning_Vault/Phase1_Month1/WeekN/dayN_<snake_case>.py
       → 规范: 见「代码文件规范」章节

[等待] Step 4: 等用户阅读并确认代码无误
       → 用户回复"没问题"/"ok"/"确认"后才继续

[异常分支] Step 4a: 错误排查循环
       → 如果用户反馈代码运行报错（包含 traceback）或结果与预期不符：
       → 必须首先要求用户提供完整报错信息。
       → 分析错误原因并提供修复后的代码片段。
       → 重新等待用户确认运行通过后，才允许进入 Step 5，绝不强行推进进度。

[自动] Step 5: 生成学习检验（Flashcards / 代码习题）
       → 3-5 道闪卡 + 1-2 道代码填空/改错题
       → 覆盖今日核心概念、API、数学推导关键步骤
       → 必须保存为实体文件：Learning_Vault/PhaseX_MonthY/WeekN/DayN_学习检验.md
       → 格式规范参考 resources/summary-template.md 的「闪卡/习题生成规范」章节
       → **题型强制要求**：针对矩阵运算、数据清洗或金融模型，必须包含至少一题"维度形状推演（Shape intuition）"（例如：(N,T) @ (T,N) 得到什么维度？）或"金融业务直觉"，以强化量化直觉。

[等待] Step 6: 用户完成检验，回复答案或自评掌握度（高/中/低）

[自动] Step 7: 根据掌握度生成总结笔记
       → 路径: Learning_Vault/Phase1_Month1/WeekN/DayN_<中文标题>总结.md
       → 规范: 见「总结笔记规范」章节
       → 掌握度低 → 在总结中增加「⚠️ 薄弱点」章节，标记需复习的知识点

[自动] Step 8: 更新 Learning_Log.md
       → 将对应 Day 的 `[ ]` 改为 `[x]`
       → 在「今日高光摘要」列写入一句话总结（从今日核心认知提炼）
→ 运行 `project/scripts/update_progress.py` 更新进度条

[提示] Step 9: 提示用户 Git 操作
       → 提示用户执行 git add + commit + push
       → 建议的 commit message 格式: "feat: Phase1/Week3/Day5 - <核心内容>"
```

### Workflow B：仅生成总结笔记

```
[自动] Step 1: 进度检测，确定目标 Day
[自动] Step 2: 读取对应 .py 代码文件
[自动] Step 3: 按总结笔记规范生成 .md 文件
[自动] Step 4: 更新 Learning_Log.md（如未打卡）
```

### Workflow C：月度计划制定

```
触发条件: 用户说"制定下个月的计划"或当前月 TODO 全部完成

[自动] Step 1: 读取当前 Phase 的目标文档（curriculum/knowledge-base/）
[自动] Step 2: 读取 Learning_Log.md，统计已完成项和薄弱点
[自动] Step 3: 读取上月 TODO 完成情况，识别未完成/偏差项
[自动] Step 4: ⚠️ 若是 Phase 交接（如 Phase 1→2），必须先触发 Workflow C+（环境扫描）
       → 将扫描报告的结论作为下一 Phase 计划制定的输入
[自动] Step 5: 生成下月 TODO_PhaseX_MonthY.md 到 curriculum/plans/ 目录
       → 格式参考现有 TODO_Phase1.md
       → 每天的任务要考虑上月薄弱点的复习安排
       → 若有环境扫描报告，需将"工具链更新建议"纳入新计划
```

### Workflow C+：Phase 过渡环境扫描（行业脉搏检查）

```
触发条件:
  1. Phase 即将结课（当前 Phase 的 TODO 完成率 ≥ 85%）
  2. 用户主动说"做一次行业扫描"/"看看最新趋势"
  3. Workflow C（月度计划制定）中检测到 Phase 交接

目的: AI 和量化行业发展迅速，地基层知识（线代/统计/金融理论）不会过时，
      但工具层和前沿层每 6-12 个月就可能有重大变化。
      此工作流确保后续 Phase 的计划不会基于过时的技术栈制定。

[自动] Step 1: 确定扫描范围
       → 读取即将进入的 Phase 目标文档（curriculum/knowledge-base/0N_PhaseN_*.md）
       → 提取该 Phase 涉及的核心技术关键词（如：回测框架、因子分析、RL 交易等）

[自动] Step 2: 执行定向搜索（Web Search + NotebookLM）
       → 围绕以下 4 个维度进行搜索：
         ① 工具链现状：该 Phase 计划使用的框架/库是否仍然活跃？有无更优替代？
            （例：VectorBT 是否还是最佳选择？Alphalens 是否已被替代？）
         ② 行业实践：目标技能在当前量化行业的真实落地程度如何？
            （例：多因子模型的工业级实践有无新范式？）
         ③ AI 融合度：LLM/Agent 在该领域的最新应用进展
            （例：LLM 选股、AI 因子挖掘是否已有成熟开源方案？）
         ④ 学习资源：有无新的优质课程/开源项目/论文值得纳入参考？

[自动] Step 3: 生成环境扫描报告
       → 路径: curriculum/plans/PhaseN_环境扫描报告_YYYYMMDD.md
       → 格式:
         # Phase N 过渡环境扫描报告
         ## 扫描日期: YYYY-MM-DD
         ## 1. 工具链评估（保留/替换/新增）
         ## 2. 行业实践动态
         ## 3. AI 融合机会
         ## 4. 推荐学习资源更新
         ## 5. 对下一 Phase 计划的具体调整建议

[等待] Step 4: 用户确认扫描报告
       → 用户可修改/补充调整建议
       → 确认后，将结论注入 Workflow C 的计划制定流程
```

### Workflow D：进度查询

```
触发条件: 用户问"我学到哪了"/"当前进度"

[自动] 执行进度检测，输出：
- 当前位置（Phase/Week/Day）
- 已完成天数/总天数（进度条）
- 本 Week 剩余任务预览
- 待复习的薄弱点（从 Learning_Log 中的标记提取）
```

### Workflow E：断点复习与冷启动 (Warm-up Review)

```
触发条件:
  1. 用户主动要求"复习"、"找找手感"、"中断很久了"
  2. Agent 在 Workflow A 进度检测时，发现距离最后一次打卡时间超过 5 天（主动提议）

[自动] Step 1: 上下文侦察（主动推断复习范围）
       → 查中断时长：确定上一次完成的阶段（如 Week 3 Day 4-5）
       → 查薄弱点：扫描之前总结笔记中的 `⚠️ 薄弱点记录`
       → 查遗忘曲线：扫描 Learning_Log.md 中 `复习回溯 (1/3/7)` 栏，提取 1/3/7 天前的内容

[等待] Step 2: 提议与确认
       → Agent 综合 Step 1 的侦察结果，向用户主动提议复习范围（而非直接让用户填空）
       → 例如："检测到您中断了 6 天，建议重点复习当时被标记为薄弱点的『协方差矩阵』，并对前 3 天的内容做快速回溯。是否同意？或者您想指定特定范围？"
       → 等待用户确认范围

[自动] Step 3: 生成增量复习包
       → 创建特定复习目录：`Learning_Vault/Reviews/YYYYMMDD_<复习主题>/`
       → 生成 1. `知识骨架_Overview.md`（严禁长篇大论，强制使用思维导图、表格对比或 API 速查表格式）
       → 生成 2. `恢复训练_Challenge.py`（实战默写题，提供带有 assert 的代码骨架，要求用户手敲填空找回手感，而非简单的选择题）

[等待] Step 4: 用户验收
       → 用户完成 Challenge，跑通断言（assert）
       → 确认找回手感后，即可衔接进入 Workflow A 开始新课
```

---

## 代码文件规范

**核心原则：代码规范随学习阶段演进，不强制固定框架。**
当前 Phase 1 的代码使用 **`#%%` cell 格式**，在 VS Code 中可逐块交互执行，同时 `python dayN.py` 可作为完整脚本运行，一份文件两用。

### 必须遵守的规定

1. **模块 docstring（必须）**：文件头部 `""" """` 说明今日核心认知跃迁、学习目标
2. **路径动态定位（必须）**：使用 `__file__` + `os.path.abspath` 定位项目根目录，禁止硬编码路径
3. **数据加载（Week3+ 必须）**：从 `Database/files/panel_50stocks.parquet` 读取面板数据
4. **`#%%` cell 划分（必须）**：
   - 每个 cell 聚焦**一个概念步骤**，不超过 15 行
   - Cell 标题格式：`# %% [N. 描述]`（如 `# %% [3. 协方差矩阵]`）
   - **每个 cell 末尾必须有 `print` 或 `assert` 输出**，让逐块执行时有可见反馈
   - 关键 cell 在 print 前加形状注释：`print(f"R.shape = {R.shape}")  # (T, N)`
5. **注释风格（教学式，三维覆盖）**：关键 cell 的注释要从三个维度解释：
   - 【数学概念】公式的定义、推导逻辑、维度说明
   - 【金融直觉】这个操作在金融业务上意味着什么
   - 【编程概念】API 的选择理由、参数含义、常见坑

### 禁止的行为

- 硬编码绝对路径（如 `D:\\project\\Bohr\\...`）
- 无注释的数学公式实现
- 不符合当前 Phase 学习目标的超前代码（如在 Phase 1 引入 VectorBT 框架）

---

## 总结笔记规范

### 文件命名

`DayN_<中文标题描述>总结.md`（参考已有笔记的命名风格）

### 内容结构（根据掌握度动态调整）

```markdown
# Week X Day Y: <中文标题> (<核心技术关键词>)

## 1. 核心认知与代码解释
[今日最核心的概念 + 关键代码片段，不是所有代码的复制粘贴]

## 2. <技术专题>（按当天内容灵活命名）
[性能对比 / API 速查 / 数学推导 / 注意事项 等]

## 3. 整体学习进度与知识关联
- **复盘前序**: 串联之前学过的内容
- **当前里程碑**: 今天打通了什么
- **预告引申**: 下一步方向

## ⚠️ 薄弱点记录（仅当掌握度为"低"时生成此章节）
[用户自评低分的知识点 + 建议的复习方法]
```

### 质量要求

- **不是代码注释的搬运**：总结要提炼"理解"，不是复制代码行
- **数学公式用 LaTeX**：`$\sigma_p^2 = w^T \Sigma w$`
- **代码片段选最关键的**：每个代码块不超过 15 行，展示核心逻辑
- **知识关联要具体**：引用具体的前序 Day（如"Day 3 推导的 Σ"）

---

## Learning_Log.md 打卡规范

Agent 负责写入打卡记录，格式参考现有表格：

```markdown
| [x] | [ ] | **Day N** | D:\project\Bohr\Learning_Vault\Phase1_Month1\WeekX\dayN_<name>.py | <一句话高光总结，提炼今日最核心的认知跃迁> |
```

**一句话总结要求**：
- **绝对不超过 60 字（严格字数限制）**，如果超出会破坏表格排版。如果生成过长，请在后台自我截断并重写。
- 推荐使用"掌握了...实现了...证明了..."的动宾短语结构紧凑表达。
- 聚焦于今天 **新学到了什么**，而不是重复任务描述
- 参考风格："初步体验了 Polars 的懒加载（pl.scan_csv），看到了熟悉的 SQL 物理执行计划"

---

## NotebookLM 集成指引

> 参考 `.agent/skills/notebooklm-mcp/SKILL.md` 了解工具用法

### 何时调用 NotebookLM

| 场景 | 动作 |
|------|------|
| 用户理解某概念有困难，需要扩展解释 | `notebook_query` 查询"个人量化入行知识库" |
| 生成检验题（Flashcards/习题）时需要补充背景知识 | `notebook_query` 获取相关概念的深层解释 |
| 用户主动提到"去 NotebookLM 查" | 立即调用对应工具 |
| 制定月度计划时需要查阅学习资源推荐 | `notebook_query` 查询资料索引 |
| 遇到高度专业或存在争议的量化前沿模型/术语（如：协方差矩阵的正定性修复、特定风格因子构建细节等） | `notebook_query` 交叉验证知识的准确性，防止 AI 自身幻觉污染教学内容。 |

### 不需要调用 NotebookLM 的场景

- 常规 Python/NumPy/Pandas API 查询
- 当天代码的具体实现细节
- 路径/文件/Git 操作

---

## 关键文件路径速查

| 文件 | 路径 |
|------|------|
| 当前月计划 | `d:\project\Bohr\curriculum\plans\TODO_Phase1.md` |
| 打卡日志 | `d:\project\Bohr\Learning_Log.md` |
| 进度更新脚本 | `d:\project\Bohr\project\scripts\update_progress.py` |
| 面板数据 | `d:\project\Bohr\Database\files\panel_50stocks.parquet` |
| Phase1 产出目录 | `d:\project\Bohr\Learning_Vault\Phase1_Month1\` |
| Phase 目标文档 | `d:\project\Bohr\curriculum\knowledge-base\0N_PhaseN_*.md` |

---

## 推荐 Commit Message 格式

```
feat: Phase1/Week3/Day5 - 特征值分解与PCA市场因子初探
docs: Phase1/Week3/Day5 - 添加总结笔记和闪卡
chore: update learning_log Week3/Day5 打卡
```
