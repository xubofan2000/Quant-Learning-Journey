# Phase 1 - Week 2 - Day 7: 面板数据压力测试总结

## 1. 几何布朗运动 (GBM)：量化模拟的通用语言

今天用来生成 50 只模拟股票的公式是：

```
P_t = P_0 × exp(Σ r_i)
r_i ~ N(μ_daily, σ_daily)
```

其中 `μ_daily` 和 `σ_daily` 由年化参数转换而来：

```python
daily_return = (annual_return - 0.5 * annual_volatility**2) * dt  # dt = 1/252
daily_vol = annual_volatility * np.sqrt(dt)
```

注意那个 `-0.5 * σ²` 的修正项——这叫做 **Itô 修正**。如果不减它，模拟出来的期望收益率会系统性地高于你设定的年化收益率。这是连续复利和离散复利之间的数学差异，Day 3 学的对数收益率正是理解它的前置知识。

**为什么不用真实数据？** 用 AKShare 批量抓 50 只真实股票有两个问题：(1) API 限频会导致脚本跑 10 分钟以上；(2) 真实数据的缺失模式不可控，无法对 Pipeline 做精确的压力测试。GBM 模拟让你完全控制"有多少缺失值、波动率多大、收益率为正还是负"，是量化研究的标准调试工具。

## 2. tqdm 进度条：批量任务的心理保障

```python
for symbol in tqdm(stock_symbols, desc="管道处理", unit="只", ncols=80):
```

`tqdm` 做的事情极其简单——在每次迭代时更新一行文字。但在批量处理 50~5000 只股票时，它是**唯一能让你区分"程序在跑"和"程序卡死了"的工具**。关键参数：
- `desc`：任务描述（左侧文字）
- `unit`：计数单位（"只/s" 比 "it/s" 直觉得多）
- `ncols`：进度条宽度（避免在窄终端里换行错乱）

## 3. 面板数据 (Panel Data) 的两种形态

### 长表 (Long Format)——推荐
```
trade_date  | symbol  | close_price | SMA_5 | daily_return
2024-01-02  | SIM0001 | 45.230      | 44.89 | 0.0123
2024-01-02  | SIM0002 | 128.550     | 127.3 | -0.0045
```
- 每一行是"一只股票在一天的数据"
- 天然适合 `groupby('symbol')` 做批量聚合
- Parquet 存储效率更高（同类型数据连续排列）

### MultiIndex 宽表
```python
df_multi = df_panel.set_index('symbol', append=True).swaplevel()
# 索引变成 (symbol, trade_date) 的二元组
```
- 用 `df_multi.loc['SIM0001']` 可以秒速切出单只股票
- 适合做跨股票的矩阵运算（Week 3 的 NumPy 协方差矩阵会用到）

**实际工程中两种格式会频繁互转**，取决于当前操作是"逐股票处理"还是"跨股票比较"。

## 4. 内存监控的方法论

```python
df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
```

- `deep=True` 很重要——不加它，Pandas 只报告索引和指针的大小（几 KB），不会深入计算字符串列等变长数据的实际内存
- 50 只股票 × 1735 天 ≈ 87,750 行，特征宽表内存约 5.6 MB
- 线性外推：5000 只股票 ≈ 560 MB，仍在 8GB 笔记本的安全线内
- 超过 2GB 时就该考虑分批处理 + 逐批写入 Parquet（Chunk Processing）

## 5. 按股票聚合验证：三大核心风险指标

```python
summary = df_panel.groupby('symbol').agg(
    annual_return=('log_return', lambda x: (np.exp(x.sum()) - 1) * 100),
    volatility=('daily_return', lambda x: x.std() * np.sqrt(252) * 100),
    max_drawdown=('close_price', lambda x: ((x / x.cummax()) - 1).min() * 100)
)
```

| 指标 | 含义 | 公式要点 |
|---|---|---|
| **年化收益率** | 持有一年赚/亏多少 | 对数收益率求和 → exp 还原（Day 3 的可加性） |
| **年化波动率** | 价格波动的剧烈程度 | 日标准差 × √252（252 个交易日/年） |
| **最大回撤** | 从峰值到谷底最惨亏几成 | `(当前价 / 历史最高价) - 1` 的最小值 |

这三个指标会在 Week 3~4 的马科维茨组合优化和 VaR 风控中反复出现。

## 6. Week 2 完结总结

Week 2 的 7 天构成了一条完整的**数据工程流水线**：

```
Day1 时序索引+填充 → Day2 滚动窗口 → Day3 对数收益率 → Day4 多表JOIN
    → Day5 Parquet存储 → Day6 OOP封装 → Day7 批量压力测试
```

产出清单：
- ✅ `DataHandler` 类：可复用的数据管道
- ✅ `clean_data.parquet`：单只 ETF 特征宽表
- ✅ `panel_50stocks.parquet`：50 只股票面板数据
- ✅ 7 份总结笔记

**Week 3 预告**：进入数学硬核地带——用 NumPy 手撸线性代数（向量点乘、协方差矩阵、马科维茨组合优化），今天生成的 50 只股票面板数据将作为 Week 3 的直接输入。
