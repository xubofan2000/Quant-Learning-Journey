# Phase 1 - Week 2 - Day 4: 多表关联与超额收益总结

## 1. SQL LEFT JOIN → Pandas `pd.merge(how='left')`

这是今天的核心映射关系：

```sql
-- SQL 写法
SELECT * FROM etf LEFT JOIN index ON etf.trade_date = index.trade_date
```

```python
# Pandas 写法
pd.merge(df_etf, df_index, on='trade_date', how='left')
```

* **LEFT JOIN 的含义**：以左表（你持仓的标的）为主干，右表（基准指数）能匹配上就贴上去，匹配不上就填 NaN。左表的每一行**绝不丢弃**。
* **为什么量化几乎总用 LEFT JOIN**：你的持仓标的每天都在产生盈亏，哪怕基准指数那天恰好没数据（节假日差异、数据源缺失），你的净值曲线也不能断。用 INNER JOIN 会把那些天直接砍掉，导致你的持仓记录出现日期空洞，累计收益计算全盘失准。

## 2. 行数膨胀陷阱（JOIN 的头号杀手）

```python
assert len(df_merged) == len(df_etf)
```

这行断言是 JOIN 操作的**生死校验**。如果右表的关联键（trade_date）存在重复值，比如同一天出现了两条记录，那么 LEFT JOIN 会对这两条都做匹配，导致左表的那一行被"复制"成两行——这叫**笛卡尔积膨胀**。

在真实的量化系统中，行数膨胀会导致：

- 收益率被重复计算，策略表现虚高
- 成交量被重复统计，风控模型失效
- DataFrame 内存暴涨，大规模回测直接 OOM

**防御策略**：每次 merge 之后，必须 `assert` 合并后行数 == 左表行数。

## 3. 超额收益 (Excess Return / Alpha)

日度超额收益用简单收益率即可（直觉清晰）：

```python
df['excess_return'] = df['etf_return'] - df['index_return']
```

但做**年度聚合**时，必须用对数收益率（Day 3 的可加性在这里直接落地）：

```python
# 对数超额收益
df['etf_log_ret'] = np.log(df['etf_close'] / df['etf_close'].shift(1))
df['index_log_ret'] = np.log(df['index_close'] / df['index_close'].shift(1))
df['excess_log_ret'] = df['etf_log_ret'] - df['index_log_ret']

# 年度聚合：对数收益率直接 sum()，再 exp() 还原
annual_alpha_log = df_clean['excess_log_ret'].resample('YE').sum()
annual_alpha_real = (np.exp(annual_alpha_log) - 1) * 100
```

**为什么不能对简单收益率直接 `.sum()`？** 简单收益率的正确累计方式是连乘 `(1+r₁)×(1+r₂)×...`，不是求和。对日度收益率做 `.sum()` 会产生系统性偏差——年化涨幅越大，偏差越明显。对数收益率没有这个问题，因为它天然具备可加性。

* **Alpha > 0**：你的标的跑赢了大盘
* **Alpha < 0**：跑输大盘
* **Alpha ≈ 0**：跟大盘同涨同跌，没有选股价值

超额收益是量化基金经理被考核的**唯一核心指标**——客户买你的基金，就是赌你能持续产出正的 Alpha。如果你的 Alpha 长期为零，客户不如去买指数基金，费率还更低。

### 实际运行结果

```
📈 2019年: +21.15%    📈 2020年: +16.84%
📉 2021年: -8.70%     📉 2022年: -7.73%
📉 2023年: -6.99%     📈 2024年: +5.08%
```

沪深300ETF 在 2019-2020 大幅跑赢上证综指（因为权重股效应），而 2021-2023 持续跑输（小盘股行情主导）。

## 4. 知识链条串联：Day 3 → Day 4

这是本周最重要的一次"知识复利"——Day 3 学的对数收益率可加性，在 Day 4 年度超额收益聚合中被直接调用。如果 Day 3 跳过了，Day 4 的年化 Alpha 就会算错。**这就是为什么计划要求按顺序推进，每天的产出都是下一天的前置依赖。**

## 5. 四种 JOIN 类型速查表

| JOIN 类型       | Pandas 参数     | 保留行               | 量化场景                   |
| --------------- | --------------- | -------------------- | -------------------------- |
| **INNER** | `how='inner'` | 只保留两表都有的日期 | ⚠️ 会丢数据，几乎不用    |
| **LEFT**  | `how='left'`  | 保留左表所有行       | ✅ 最常用，持仓标的为主    |
| **RIGHT** | `how='right'` | 保留右表所有行       | 🔁 等价于交换表顺序做 LEFT |
| **OUTER** | `how='outer'` | 保留双方所有日期     | 🔍 数据审计/排查用         |

## 6. 自主拓展：上证指数落盘 DuckDB

你在练习之外自主完成了一件很有价值的事——把 AKShare 抓取的上证指数数据直接写入了 DuckDB 的 `szzs` 表。这意味着下次做 JOIN 时，两张表都可以从本地数据库读取，不再依赖网络 API 的实时连接。这是工业级 ETL 管道的标准做法：**先落盘，再分析**。

> ⚠️ 注意你在运行时遇到了一次 `IOException: 另一个程序正在使用此文件`。这是因为你的 `test.py` 用不带 `read_only=True` 的方式打开了 DuckDB，占着写锁没释放。DuckDB 的单写多读机制只允许同一时刻一个写连接。解决方法：写入完毕后确保 `conn.close()`，或者在只读场景下始终加 `read_only=True`。

## 7. Day 5 预告

明天将进入 **Parquet 格式**——量化界的标配存储架构。你今天 JOIN 完成的这张"ETF + 指数"宽表，明天会被压缩保存为 `.parquet` 文件。相比 CSV：体积缩小 3~5 倍，读取速度快 10~50 倍，而且 DuckDB 可以直接 `SELECT * FROM 'file.parquet'` 零拷贝查询。
