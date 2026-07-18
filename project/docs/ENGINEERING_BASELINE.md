# 工程基线

## 环境

使用项目虚拟环境并固定实际运行的直接依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r project/requirements/requirements-core.txt
python -m unittest discover -s project/tests -v
```

`project/requirements/requirements-core.txt` 固定当前基础课程环境。进入统计/研究阶段前，把本地实际验证的版本补入相应依赖清单；报告必须记录 Python、依赖、数据版本和完整命令。

## 代码分层

| 层 | 位置 | 允许内容 | 禁止内容 |
| --- | --- | --- | --- |
| 教学/恢复 | `Learning_Vault/` | 单概念脚本、填空、解释和历史记录 | 冒充可复用生产模块或正式研究结论 |
| 可复用模块 | 后续独立源码目录（Week 3 创建并记录） | 纯计算、数据契约、明确 API | import 时读取文件、打印演示、运行实验 |
| 正式研究 | `experiments/` | 研究卡、配置、数据版本、结果 | 把临时教学输出当最终证据 |
| 派生报告 | `reports/` 或项目约定目录 | 可由源代码重建的图表/报告 | 作为唯一事实源 |

## 质量门槛

| 层级 | 要求 |
| --- | --- |
| 学习脚本 | 可使用断言帮助理解，但失败必须使进程非零 |
| 可复用模块 | 用显式 `ValueError`/`TypeError` 等校验输入；不能依赖可被 `python -O` 关闭的 `assert` |
| 核心测试 | 用 `unittest` 覆盖正常、边界、非法输入和金融时间顺序 |
| 数据处理 | 校验唯一键、日期范围、缺失率、重复行和输出行数 |
| 研究结果 | 记录配置、随机种子、数据版本和完整运行命令 |
| 提交前 | 运行项目审计与相关测试；不提交大数据、密钥或派生报告 |

## 强制修复清单（纳入 `NEXT_12_WEEKS.md` Week 3-8）

1. 用显式 seed 或 `hashlib` 派生稳定 seed，禁止用跨进程不稳定的 `hash(symbol)`。
2. 研究特征禁止可能引入未来信息的 `bfill`；首期缺失应丢弃、保持缺失或使用当时可得的业务规则。
3. 对账、测试或关键质量检查失败必须抛出异常/返回非零，不能捕获后只打印。
4. 把 `PortfolioMath` 等纯逻辑与 Parquet 读取、绘图、演示和结果筛选分离。
5. 默认序列参数使用 `None` 或不可变对象，避免 `list[int] = [5, 20]`。
6. 只捕获预期异常；不得宽泛捕获所有异常后静默降级。
7. 为收益率、协方差、组合风险、因子滞后、交易成本和样本外切分增加测试。
8. 真实数据与模拟数据必须在 schema、路径、README 和报告中同时标识。

这些项目是学习任务，不由 AI 一次性代写全部答案；每个修复都需要学习者独立实现、故障注入和口述验收。

## 数据与实验目录约定

- `Database/raw/`：不可修改的原始提取；保存来源、参数和提取日期。
- `Database/processed/`：可由原始数据重新构建的中间数据。
- `Learning_Vault/`：教学脚本、检验和总结。
- `experiments/`：具备研究卡、配置和结果的正式研究实验；进入 Phase 2 时创建。
- `reports/`：本地派生报告，不作为事实源，不提交 Git。

## 自动检查与 CI 门槛

当前治理检查命令：

```powershell
python project/scripts/project_audit.py
python project/scripts/curriculum_audit.py
python -m unittest discover -s project/tests -v
```

Week 3 退出前，GitHub Actions 必须安装实际依赖并运行量化核心测试，而不只运行进度/课程治理测试。需要私有数据或凭据的测试必须使用小型固定 fixture，不得在 CI 中伪装覆盖。

## Phase 过渡检查

每个 Phase 开始前检查官方文档、依赖维护状态和适用规则，记录日期、来源与决定。涉及交易接口或监管时，必须以当时的官方资料为准，并保持模拟模式直到人工审批。
