"""
恢复训练_Challenge.py - Phase 1 冷启动复习挑战

本文件为填空练习，包含 Week 1-3 的核心逻辑。
请补充被标记为 "TODO" 的代码，并在当前目录下运行此文件：
    python 恢复训练_Challenge.py
当所有 assert 断言通过时，代表你已成功找回手感！
"""

import os
import time
import numpy as np
import pandas as pd
import duckdb
from scipy.linalg import eigh

# 动态定位项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))

db_path = os.path.join(project_root, 'Database', 'files', 'market_data.duckdb')
parquet_path = os.path.join(project_root, 'Database', 'files', 'panel_50stocks.parquet')

# ==========================================
# 🧩 Challenge 1: DuckDB 查询与对数收益率时间可加性 (Week 1 & Week 2)
# ==========================================
print("🧩 Challenge 1: 开始进行时序对数收益率校验...")

# 从 DuckDB 中读取 'sh510300' 2024年的日线收盘价
conn = duckdb.connect(db_path, read_only=True)
df_etf = conn.sql("""
    SELECT trade_date, close_price 
    FROM etf_daily_kline 
    WHERE symbol = 'sh510300'
      AND trade_date >= '2023-12-01' -- 多取一个月用于计算前向收益
    ORDER BY trade_date
""").df()
conn.close()

df_etf['trade_date'] = pd.to_datetime(df_etf['trade_date'])
df_etf.set_index('trade_date', inplace=True)

# TODO 1: 计算简单收益率 simple_return 与 对数收益率 log_return
# 提示: 简单收益率用 pct_change()，对数收益率用 np.log(close / close.shift(1))
df_etf['simple_return'] = None
df_etf['log_return'] = None

# 筛选出 2024 年的数据进行可加性校验
df_2024 = df_etf.loc['2024-01-01':'2024-12-31'].dropna()
last_price_2023 = df_etf.loc[:'2023-12-31', 'close_price'].iloc[-1]
ground_truth_ytd = df_2024['close_price'].iloc[-1] / last_price_2023 - 1

# TODO 2: 分别用两种收益率计算 2024 全年 YTD 累计收益率
# 提示：简单收益率用 (1 + r).prod() - 1，对数收益率用 np.exp(r.sum()) - 1
cum_simple = None
cum_log = None

assert np.isclose(cum_simple, ground_truth_ytd), "简单收益率累计结果不正确！"
assert np.isclose(cum_log, ground_truth_ytd), "对数收益率累计结果不正确！"
print("✅ Challenge 1 通过：对数收益率的时间可加性验证完美！")


# ==========================================
# 🧩 Challenge 2: 缺失值填充与特征工程 (Week 2)
# ==========================================
print("\n🧩 Challenge 2: 开始进行缺失值清洗与时序特征计算...")

# 加载 50 只股票的面板数据，并筛选其中 5 只股票
df_panel = pd.read_parquet(parquet_path)
selected = ['SIM0001', 'SIM0010', 'SIM0020', 'SIM0035', 'SIM0050']
df_sub = df_panel[df_panel['symbol'].isin(selected)].copy()

# 透视成以 trade_date 为行索引，symbol 为列的宽表
df_returns = df_sub.pivot_table(
    index='trade_date',
    columns='symbol',
    values='daily_return'
)

# 故意挖一些空（模拟停牌）
np.random.seed(42)
mask = np.random.rand(*df_returns.shape) < 0.05
df_dirty = df_returns.mask(mask)
assert df_dirty.isna().sum().sum() > 0, "测试脏数据没有生成空值！"

# TODO 3: 请使用金融实盘的常用填充逻辑（前向填充 ffill，若首日仍缺失则用后向填充 bfill 补齐）
# 提示: 链式调用 ffill() 和 bfill()
df_cleaned = None

assert df_cleaned.isna().sum().sum() == 0, "清洗后仍有缺失值！"

# TODO 4: 计算 SIM0001 的 5 日移动平均收益率 (Rolling SMA)
# 提示: 使用 rolling() 和 mean()
sim0001_sma5 = None

# 验证滚动窗口前 4 天应为 NaN，第 5 天开始有值
assert sim0001_sma5.iloc[3] is np.nan or pd.isna(sim0001_sma5.iloc[3]), "滚动窗口前四天不应有值！"
assert not pd.isna(sim0001_sma5.iloc[4]), "第5天应当有值！"
print("✅ Challenge 2 通过：时序填充与 Rolling 特征计算成功！")


# ==========================================
# 🧩 Challenge 3: 矩阵乘法维度与手撸协方差矩阵 (Week 3)
# ==========================================
print("\n🧩 Challenge 3: 矩阵维度推演与协方差矩阵计算...")

R = df_cleaned.values  # shape: (T, N)
T, N = R.shape

# 📌 维度形状推演自测 (Shape Intuition)
# 请填入矩阵乘法或运算后的预期 Shape 维度元组
# TODO 5: 填入正确的 Shape 形状
shape_R = None       # 代表 R 的 shape
shape_R_T_R = None   # 代表 R.T @ R 的 shape

# 验证维度直觉
assert shape_R == (T, N), f"R 的形状应为 ({T}, {N})，而不是 {shape_R}"
assert shape_R_T_R == (N, N), f"R.T @ R 的形状应为 ({N}, {N})，而不是 {shape_R_T_R}"

# TODO 6: 手工推导协方差矩阵 Sigma_manual
# 公式: \Sigma = \frac{1}{T-1} * (R - \mu)^T @ (R - \mu)
# 其中 \mu 是每个资产的均值向量 (shape 为 (N,))，注意 R - \mu 发生广播
mu = None
R_centered = None
Sigma_manual = None

# 使用 numpy 内置 API 进行对比校验
Sigma_np = np.cov(R, rowvar=False)

assert np.allclose(Sigma_manual, Sigma_np, rtol=1e-8), "手撸协方差矩阵与 numpy API 结果不符！"
print("✅ Challenge 3 通过：维度推演无误，手推协方差矩阵验证成功！")


# ==========================================
# 🧩 Challenge 4: 组合方差二次型与主成分分析 (Week 3)
# ==========================================
print("\n🧩 Challenge 4: 二次型组合方差计算与特征值分解...")

# 给定一个等权重分配的组合 w_equal
w_equal = np.ones(N) / N  # shape: (N,)

# TODO 7: 用二次型公式计算等权组合方差 portfolio_var_analytical
# 数学公式: \sigma_p^2 = w^T @ \Sigma @ w
# 提示: 使用 np.dot 或 @ 运算符
portfolio_var_analytical = None

# 双重验证：将收益率矩阵与权重相乘得到组合每日收益序列，然后直接求样本方差
portfolio_ret_series = R @ w_equal
portfolio_var_empirical = np.var(portfolio_ret_series, ddof=1)

assert np.isclose(portfolio_var_analytical, portfolio_var_empirical, rtol=1e-8), "组合方差二次型解析解与实证方差不吻合！"

# TODO 8: 对协方差矩阵进行特征分解，并提取最大特征值及其特征向量
# 提示: 使用 scipy 的 eigh (适合对称矩阵)
eigenvalues, eigenvectors = None, None

# eigenvalues 默认升序排列，提取最大特征值及对应的特征向量 (PC1)
max_eigenval = None
pc1 = None

# 验证 PC1 的金融直觉：PC1 的所有权重符号应该一致（同正或同负），表示它提取了市场的 Beta 系统性同向波动
# 我们强制将其归一化为正数，以反映市场因子的方向
if pc1 is not None and np.sum(pc1) < 0:
    pc1 = -pc1

assert np.all(pc1 > 0), "市场 Beta 因子 (PC1) 各股票的权重应该全为正值，反映系统性大盘风险！"
print("✅ Challenge 4 通过：资产组合方差计算与主成分系统性因子提取成功！")


# ==========================================
# 🧩 Challenge 5: 广播机制无循环向量化回测 (Week 3)
# ==========================================
print("\n🧩 Challenge 5: 开始 1000 个策略的批量无循环向量化回测...")

# 生成 M 个随机策略的权重矩阵 W
M = 1000
np.random.seed(42)
W = np.random.dirichlet(np.ones(N), size=M)  # shape: (M, N)

# 📌 维度形状推演自测 (Shape Intuition)
# 我们需要对 M 个策略在 T 天的每日收益率进行批量计算
# 收益率矩阵 R: (T, N)，权重矩阵 W: (M, N)
# TODO 9: 采用矩阵乘法，一行代码算出所有策略在所有交易日的收益率矩阵 R_all_portfolios
# 结果 Shape 必须是 (T, M) —— 每一列代表一个策略的每日收益率序列
R_all_portfolios = None

assert R_all_portfolios.shape == (T, M), f"回测矩阵 shape 应为 ({T}, {M})，而不是 {R_all_portfolios.shape}"

# TODO 10: 向量化计算所有策略每日的累计收益净值曲线 Equity_curves
# 提示: 累计净值 = ∏ (1 + r_t)，使用 np.cumprod(..., axis=0) 沿着时间轴累乘
Equity_curves = None

assert Equity_curves.shape == (T, M), "累计净值曲线 shape 不正确！"
# 验证首日净值应该都在 1 附近（即 1 + 收益率）
assert np.all(Equity_curves[0] > 0.8) and np.all(Equity_curves[0] < 1.2), "净值计算起始点有误！"
print("✅ Challenge 5 通过：多策略向量化回测与累计净值计算跑通！")

print("\n" + "=" * 60)
print("🎉 恭喜你跑通了全部 Challenge 断言！冷启动复习成功，手感已拉满！")
print("=" * 60)
