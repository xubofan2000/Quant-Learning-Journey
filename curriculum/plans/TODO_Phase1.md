# Phase 1 历史计划：基建与数理（已由能力验收路线接管）

此文件保留 2026 年 3-4 月的原始任务和勾选记录，用于审计历史，不再是当前每日执行入口。当前计划见 `NEXT_12_WEEKS.md`，当前能力见 `JOB_CAPABILITY_MATRIX.md`。

历史 `[X]` 只表示当时计划/日志曾确认，并不证明学习者能独立实现、通过测试和解释金融假设。既有代码、总结和 Git 历史保留；未通过的新验收不得沿用旧“完成”结论。

原计划前两周用于把 SQL 经验迁移到 Python/DuckDB/Pandas/Polars，后两周用于把数学公式转译为 NumPy/SciPy 代码。旧的按天节奏已由 12-15 小时/周的能力周期替代。

> 💡 **学习指引**：每天的任务后方均附带了你需要去 **NotebookLM（AI驱动量化转型知识库）** 向 AI 提问或查阅的指定参考文档。

## Week 1: SQL 到 Pandas 的思维映射与本地环境跑通

**🎯 里程碑产出 (Milestone)**：编写一个 Python 脚本，将本地 CSV 载入 DuckDB，执行复杂 SQL 聚合，并用 Pandas 实现完全一致的结果对比。

### Day 1

- [X] 任务：完成 DuckDB 本地环境安装，了解与 SQLite 的差异（列式计算 vs 行式）。(📚 查阅 NotebookLM: `DuckDB Python 官方文档 -> Installation & Overview`)
- [X] 产出：一段能在本地运行并创建空 DuckDB 数据库的 Python 脚本。

### Day 2

- [X] 任务：利用 Python 原生能力或 Faker 库，生成随机的 10 万行股票交易模拟数据（包含 date, ticker, price, volume），存为 CSV。
- [X] 产出：本地生成成功并输出 `dummy_market_data.csv` 文件的脚本。

### Day 3

- [X] 任务：用 DuckDB Python API 直接读取该 CSV，利用你的老本行，执行包含 `GROUP BY ticker` 和 `ORDER BY` 的 SQL 查询。(📚 查阅 NotebookLM: `DuckDB Python 官方文档 -> Relational API / DataFrames`)
- [X] 产出：打印输出每日最高价和总成交量的查询结果日志。

### Day 4

- [X] 任务：引入 Pandas，对比 SQL 中 `WHERE`、`SELECT`、`GROUP BY` 在 Pandas `DataFrame` 中的映射写法。(📚 查阅 NotebookLM: `Python for Data Analysis -> Chapter 10: Data Aggregation and Group Operations`)
- [X] 产出：用 Pandas 的 `.loc` 和 `.groupby()` 重写 Day 3 的查询，并建立个人的 SQL vs Pandas 语法对照表。

### Day 5

- [X] 任务：浅尝 Polars 的懒加载（Lazy Evaluation）特性。感受列式处理与多线程在量化回测中的速度优势。(📚 查阅 NotebookLM: `DuckDB 官方文档与 Polars 交互概念`)
- [X] 产出：一段使用 Polars 读取 CSV 并执行与前天相同聚合操作的代码，并对比耗时。

### Day 6（历史长时段任务）

- [X] 任务：实战！从类似 yfinance 或 tushare 的免费接口抓取真实的某只指数 ETF 5 年日线数据，持久化存入 DuckDB 物理文件(`.duckdb`)。(📚 查阅 NotebookLM: `Python for Data Analysis -> Chapter 6: Data Loading, Storage`)
- [X] 产出：本地成功生成包含真实连贯交易数据的 `.duckdb` 数据库文件。

### Day 7（历史长时段任务）

- [X] 任务：自动化对账校验。用 SQL 在 DuckDB 算出月度平均收盘价，再用 Pandas 从该库读取全图后用 `.resample('M').mean()` 计算，断言两者结果一致。(📚 查阅 NotebookLM: `Python for Data Analysis -> Chapter 11: Time Series - Resampling`)
- [X] 产出：包含 `assert` 断言通过用例的对账 Python 脚本。

## Week 2: 金融时序预处理与特征工程基建

**🎯 里程碑产出 (Milestone)**：完成一份“包含缺失值、停牌日”的脏数据清洗脚本，输出标准的对齐特征表并保存为 Parquet 进行加速。

### Day 1

- [X] 任务：学习 Pandas 的时序索引（DatetimeIndex）与前向/后向填充机制（`ffill`/`bfill`）。(📚 查阅 NotebookLM: `Python for Data Analysis -> Chapter 7: Data Cleaning and Preparation`)
- [X] 产出：给上周的真实股票数据代码里“随机挖空”（模拟停牌/断网），然后用上一交易日收盘价逻辑补全。

### Day 2

- [X] 任务：理解 SQL 的 Window Function（窗口函数）在 Python 中的等价物 `.rolling()` 和 `.shift()`。(📚 查阅 NotebookLM: `Python for Data Analysis -> Chapter 11: Time Series - Moving Window Functions`)
- [X] 产出：给 DataFrame 增加两列：计算过去 5 日和 20 日的移动平均线 (SMA)。

### Day 3

- [X] 任务：弄清楚量化中“对数收益率”与“普通收益率”的差别。
- [X] 产出：使用 Pandas 原生函数 `.pct_change()` 并结合 `numpy.log` 生成准确的每日收益率序列。

### Day 4

- [X] 任务：多表关联（Join/Merge），体会 SQL `LEFT JOIN` 与 Pandas `.merge(how='left')` 的一致性及避坑（防止行数膨胀）。(📚 查阅 NotebookLM: `Python for Data Analysis -> Chapter 8: Data Wrangling: Join, Combine`)
- [X] 产出：抓取沪深300（或标普及准），按日期作为 Key，与个股数据进行 Left Join 严格对齐。

### Day 5

- [X] 任务：拥抱量化界标配存储架构——Parquet 格式。比起 CSV 的体积与反序列化速度优势在哪？怎么联手 DuckDB 使用？(📚 查阅 NotebookLM: `DuckDB 官方文档 -> Data Import/Export (Parquet)`)
- [X] 产出：将清洗并关联好的宽表 DataFrame 直接压缩保存为 `clean_data.parquet` 文件。

### Day 6（历史长时段任务）

- [X] 任务：项目面向对象重构。串联前两周，用面向对象 (OOP) 封装一个 `DataHandler` 类，暴露 `load_raw`, `clean`, `save_feature` 等标准方法。
- [X] 产出：一个脱离了面条代码（Spaghetti code）的结构化 `data_pipeline.py`。

### Day 7（历史长时段任务）

- [X] 任务：基建初次压力测试。尝试循环抓取/生成 50 只股票的数据并合并，测试你的 Pipeline 的内存占用，引入 `tqdm` 加上进度条监控体验。(📚 查阅 NotebookLM: 对 Pandas 的大规模数据处理与向量化进行摘要提问)
- [X] 产出：输出含有 50 个股票维度（MultiIndex或长表形式）的复合面板数据。

## Week 3: 从理论到代码 - 线性代数与资产组合映射

**历史里程碑产出**：不调用现成库，手写 NumPy 矩阵运算，计算包含 3 只股票的组合收益率与协方差矩阵。该产出需要重新通过独立恢复训练后才能升级为能力证据。

### Day 1

- [X] 任务：理解向量与矩阵点乘。直接将“股票配置权重”看作 $1 \times N$ 向量，“每日收益”看作 $N \times 1$ 向量。(📚 查阅 NotebookLM: `Mathematics for Machine Learning -> Chapter 2: Linear Algebra (Vectors & Matrices)`)
- [X] 产出：使用 `np.array` 定义 3 权重与当日收益，用一行 `np.dot` / `@` 算出当天的资金曲线总收益。

### Day 2

- [X] 任务：理解按元素乘法（`*`）与矩阵叉乘（`@`）的区别。意识到 Pandas 底层运算剥开就是 NumPy。
- [X] 产出：构造 50 天 x 50 只股票的收益矩阵，分别使用 `for` 循环与 Numpy 矩阵运算求和，打印耗时差异。

### Day 3

- [X] 任务：代码手撸协方差矩阵（Covariance Matrix）。这是马科维茨风控衡量资产间相关性的心脏步骤。(📚 查阅 NotebookLM: `Mathematics for Machine Learning -> Chapter 6: Probability and Distributions (Covariance)`)
- [X] 产出：调用 `np.cov()` 与手工推导公式两种方式，算出历史收益的相关结构，结果进行 assert 验证。

### Day 4

- [X] 任务：马科维茨理论的程序化表达：将组合方差公式数学语言 $\sigma_{p}^2 = w^T \Sigma w$ 转义为代码。
- [X] 产出：一行代码实现 $w^T \cdot \Sigma \cdot w$，准确输出你持仓组合的波动率评估数值。

### Day 5

- [X] 任务（历史记录）：特征值与特征向量的金融含义（PCA 最大方差方向初探）。PCA 的 PC1 不能仅凭模拟数据或与等权组合相关就被“证明”为市场 Beta；命名需结合真实数据、载荷结构、基准和稳定性证据。(📚 查阅 NotebookLM: `Mathematics for Machine Learning -> Chapter 4: Matrix Decompositions (Eigendecomposition & PCA)`)
- [X] 产出：通过 `scipy.linalg.eigh` 解剖你生成的协方差矩阵，提取最大的特征值（最大震荡方向）。

### Day 6（历史长时段任务）

- [X] 任务（历史记录）：利用 NumPy 广播机制完成连续 252 个交易日的固定权重组合批量收益计算。
- [X] 历史产出：不用 `for` 循环生成批量收益与净值曲线。`R @ W.T` 仅是向量化演示，不是包含信号、实际持仓、成交、成本、无法成交、现金和基准的完整回测。

### Day 7（已替代为 Week 1 + Week 3 验收）

- [ ] 任务：先不看原代码完成最新恢复训练；Week 3 再把纯计算、数据 I/O 和演示拆开，修复 `assert` 输入校验、可变默认参数和导入副作用。
- [ ] 产出：独立完成的恢复训练、可导入核心模块、15-25 个有效测试和口述验收。现有 `day7_portfolio_math_module.py` 只是待验收历史输入，不得自动勾选。

## Week 4：概率统计与风险分布（旧安排已由 `NEXT_12_WEEKS.md` Week 2 替代）

**🎯 里程碑产出 (Milestone)**：利用 Scipy 分布拟合真实数据，计算出个股的 95% 历史 VaR（在险价值），并用 matplotlib 渲染分布直方图。

### Day 1

- [ ] 任务（历史计划，已替代）：讨论正态分布对金融收益厚尾和极端行情刻画不足的条件与后果。(📚 查阅 NotebookLM: `Mathematics for Machine Learning -> Chapter 6: Gaussian Distribution`)
- [ ] 产出：拉取真实的股票收益，与理想的均匀正态分布生成结果在直方图上叠图比对。

### Day 2

- [ ] 任务（历史计划，已替代）：计算均值（Expected Value）、方差（Variance）、偏度（Skewness）、峰度（Kurtosis）。
- [ ] 产出：编写专门诊断个股的统计面函数，若峰度很高则直接 Print “存在厚尾极端风险”。

### Day 3

- [ ] 任务（历史计划，已修正）：P-value 与假设检验。p-value 只能量化在指定零假设、抽样机制和模型前提下观察到当前或更极端结果的证据，不能证明策略赚钱不是运气。(📚 查阅 NotebookLM: “假设检验与 p-value 的本质”)
- [ ] 历史产出（已替代）：运行一元线性回归，报告 Alpha、p-value、效应大小、置信区间、残差诊断与假设限制。

### Day 4

- [ ] 任务（历史计划，已替代）：理解 VaR (Value at Risk) 及历史分位数法的直观、假设与局限。
- [ ] 产出：只用一行 Pandas 接口 `.quantile(0.05)` 直接拿到个股日度单边极端风险值。

### Day 5

- [ ] 任务：参数 VaR (Parametric VaR) 与正态假设推演。代入标准的 z-score 公式反推概率分布边缘。
- [ ] 产出：手工用公式 $VaR = \mu - 1.645 \cdot \sigma$ 计算（95%置信度下单边1.645）并与昨天的蛮力历史 VaR 对比误差。

### Day 6（历史长时段任务，已修正）

- [ ] 任务（历史计划，已替代）：实现 Monte Carlo/GBM，用于情景模拟、风险分析和模型理解，并讨论模型风险。
- [ ] 历史产出（已替代）：在明确参数与分布假设下模拟 30 天的 1000 条路径；不得称为可靠预测未来股价。

### Day 7（历史长时段任务，已替代）

- [ ] 任务（历史计划，已替代）：串联 ETF 数据、组合风险、厚尾、VaR/CVaR 与情景模拟，产出明确假设和限制的统计报告。
- [ ] 历史产出（已替代）：可复现的研究报告；项目质量以数据契约、测试、样本外、成本、局限和讲解能力验收，不以 GitHub 星数验收。
