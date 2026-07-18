# 学习证据与历史摘要追踪

本文件保留既有学习记录、代码索引和复习记录，但不再把打卡天数作为主要进度。经过验收的当前能力以 `curriculum/plans/JOB_CAPABILITY_MATRIX.md` 为准，未来任务以 `curriculum/plans/NEXT_12_WEEKS.md` 为准。

## 当前审计结论（2026-07-18）

- 历史记录显示 20/28 个 Day 被确认；这只说明计划、打卡与部分文件曾经一致，不等于掌握。
- Week 3 Day 7 已有代码和学习检验，但计划与日志均未完成，且没有正式总结或独立单元测试。
- 最新 Week 3 恢复训练仍未填写；实际运行在第一项 Shape 断言失败。
- 当前仓库未发现任何一项能力同时具备“独立实现 + 测试通过 + 能解释”的完整证据，因此本轮不新增“掌握”标记。
- 下一具体任务：不看历史 Day 代码，完成 `Learning_Vault/Reviews/20260718_Week3_矩阵运算与PortfolioMath/恢复训练_Challenge.py`，保留失败和修复记录。

> 下方每日表格是历史证据索引。原有 `[x]` 不删除、不回写为能力等级；其中的夸张或不准确表述由当前研究协议和知识库勘误覆盖。

---

## 历史每日记录

> *每天学习完，花 2 分钟在这里写两句你今天 Get 到的重点，或者粘贴一段让你爽到的报错/运行结果。*

<details open>
<summary><b>🔥 Week 1 / SQL 到 Pandas 的思维映射与本地环境跑通</b></summary>

| 打卡 | 复习回溯 (1/3/7) | Day             | 产出成果定位                                                            | 今日高光摘要 (Highlights & Bugs)                                                                                                                                         |
| ---- | ---------------- | --------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [x]  | [ ]              | **Day 1** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week1\day1_duckdb_init.py  | 理解了 Python 相对路径受终端执行目录影响，学会了用 `__file__`动态定位；认识到 DuckDB 是二进制文件，不能用文本编辑器直接打开。                                          |
| [x]  | [ ]              | **Day 2** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week1\day2_csv_gen.py      | 切忌硬编码，用动态寻址__file__和相对路径的方式编程；<br />.gitignore文件用来告诉git哪些文件（夹）不要同步                                                                |
| [x]  | [ ]              | **Day 3** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week1\day3_sql_query.py    | 体验了 DuckDB 直接将 CSV 路径作为表名进行零拷贝查询，学习了列修剪带来的极致 I/O 优化。                                                                                   |
| [x]  | [ ]              | **Day 4** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week1\day4_pandas_map.py   | 掌握了 SELECT/WHERE/GROUP BY 的 Pandas 链式调用映射。深刻体会到 Pandas `read_csv` 的高昂内存反序列化成本，明确了 DuckDB 负责 I/O 降维、Pandas 负责内存运算的工程边界。 |
| [x]  | [ ]              | **Day 5** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week1\day5_polars_test.py  | 初步体验了 Polars 的懒加载（pl.scan_csv），看到了熟悉的 SQL 物理执行计划，理解了谓词下推（Predicate Pushdown）是如何节约内存的。                                         |
| [x]  | [ ]              | **Day 6** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week1\day6_real_data.py    | 实战了真实的金融数据爬虫。摒弃了 MySQL 的行级 UPSERT 泥潭，运用了数据仓库经典的『查询水位线 + DELETE & INSERT 幂等覆盖』架构，<br />将沪深300 ETF 五年数据成功落盘。     |
| [x]  | [ ]              | **Day 7** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week1\day7_assert_check.py | 掌握了金融数据的本地可视化查验，并独立编写了双引擎（DuckDB & Pandas）对账风控脚本，彻底打通量化数据底座！                                                                |

</details>

<details>
<summary><b>🔥 Week 2 / 金融时序预处理与特征工程基建</b></summary>

| 打卡 | 复习回溯 (1/3/7) | Day             | 产出成果定位                                                             | 今日高光摘要 (Highlights & Bugs)                                                                                                                                                                                   |
| ---- | ---------------- | --------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [x]  | [x]              | **Day 1** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week2\day1_data_cleaning.py |                                                                                                                                                                                                                    |
| [x]  | [x]              | **Day 2** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week2\day2_rolling_shift.py | 今日成功将 SQL 的窗口函数（Window Function）与偏移逻辑完美映射至 Pandas，利用 `.rolling()` 和 `.shift()` 实现了多周期移动均线（SMA）、收益率交叉校验及金叉死叉信号探测，彻底打通了金融时间序列的滚动特征基建。 |
| [x]  | [x]              | **Day 3** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week2\day3_log_returns.py   | 全年收益率应该用今年年末-去年年末。就像在计算首日的收益率时也是用今年第一天的收盘价-去年最后一天的收盘价。<br />对数收益率可以累加。                                                                               |
| [x]  | [x]              | **Day 4** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week2\day4_join_merge.py    | pd.merge等效于SQL的JOIN                                                                                                                                                                                            |
| [x]  | [x]              | **Day 5** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week2\day5_parquet.py       | duckdb配合parquet数据抽取是最快的组合，其次是to_parquet                                                                                                                                                            |
| [x]  | [x]              | **Day 6** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week2\day6_data_pipeline.py | 串联了之前所有的核心要点，实现了真正可用的数据pipline类                                                                                                                                                            |
| [x]  | [x]              | **Day 7** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week2\day7_stress_test.py   | 标准量化模拟数据生成的流程还考虑到伊藤引理的影响，由年到日                                                                                                                                                         |

</details>

<details>
<summary><b>🔥 Week 3 / 从理论到代码 - 线性代数与资产组合映射</b></summary>

| 打卡 | 复习回溯 (1/3/7) | Day             | 产出成果定位                                                                     | 今日高光摘要 (Highlights & Bugs)                                                                                   |
| ---- | ---------------- | --------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| [x]  | [x]              | **Day 1** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week3\day1_vector_dot_product.py    | 时间序列上加总用 Log Return，横截面加权求和用 Simple Return                                                        |
| [x]  | [ ]              | **Day 2** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week3\day2_elementwise_vs_matmul.py | *是broadcasting(展开)保留明细，@是contraction(坍缩)汇总；Pandas底层就是NumPy多一步索引对齐开销；分散化效应数学证明 |
| [x]  | [ ]              | **Day 3** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week3\day3_covariance_matrix.py     | 协方差矩阵由各股票面板转宽表后先去除每支股票的均值，除以t-1后再通过矩阵乘法得到N*N的协方差矩阵                     |
| [x]  | [ ]              | **Day 4** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week3\day4_portfolio_variance.py    | σ²_p = w^T @ Σ @ w，实现了基础理论到二次型的转换，并配合蒙特卡洛随机权重生成了散点图版风险有效前沿。 |
| [x]  | [ ]              | **Day 5** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week3\day5_eigendecomposition_pca.py | 掌握了 eigh 分解 Σ=QΛQᵀ，提取方差解释率，证明 PC1≈市场Beta因子，验证重构误差达机器精度。 |
| [x]  | [ ]              | **Day 6** | D:\project\Bohr\Learning_Vault\Phase1_Month1\Week3\day6_broadcasting_backtest.py | 用 `R @ W.T` 一行代码完成 1 万种策略 × 252 天的向量化回测，Broadcasting + cumprod 生成全量净值曲线，性能碾压 for 循环 100x+。 |
| [ ]  | [ ]              | **Day 7** | `Learning_Vault/.../Week3/`                                                    | [待填写]                                                                                                           |

</details>

<details>
<summary><b>🔥 Week 4 / 从理论到代码 - 概率统计与风险分布</b></summary>

| 打卡 | 复习回溯 (1/3/7) | Day             | 产出成果定位                  | 今日高光摘要 (Highlights & Bugs) |
| ---- | ---------------- | --------------- | ----------------------------- | -------------------------------- |
| [ ]  | [ ]              | **Day 1** | `Learning_Vault/.../Week4/` | [待填写]                         |
| [ ]  | [ ]              | **Day 2** | `Learning_Vault/.../Week4/` | [待填写]                         |
| [ ]  | [ ]              | **Day 3** | `Learning_Vault/.../Week4/` | [待填写]                         |
| [ ]  | [ ]              | **Day 4** | `Learning_Vault/.../Week4/` | [待填写]                         |
| [ ]  | [ ]              | **Day 5** | `Learning_Vault/.../Week4/` | [待填写]                         |
| [ ]  | [ ]              | **Day 6** | `Learning_Vault/.../Week4/` | [待填写]                         |
| [ ]  | [ ]              | **Day 7** | `Learning_Vault/.../Week4/` | [待填写：恭喜通过第一阶段大考！] |

</details>
