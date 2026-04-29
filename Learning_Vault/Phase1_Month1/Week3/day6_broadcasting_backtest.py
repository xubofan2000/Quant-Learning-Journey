"""
day6_broadcasting_backtest.py - Week 3 Day 6: NumPy 广播机制与向量化回测

核心认知跃迁：
    在量化回测中，我们经常需要评估成百上千种策略（不同权重组合）在几年的历史数据上的表现。
    如果用 for 循环：for 策略 in 所有策略: for 交易日 in 所有交易日: ... 
    在 Python 中会导致灾难性的性能瓶颈。

    今天，我们将彻底抛弃循环，利用 NumPy 的矩阵乘法和 Broadcasting（广播机制），
    一行代码计算出 M 种组合在 T 个交易日的全部收益率，
    再用一行代码生成这 M 种组合的全量资金净值曲线（NAV）。

    这就是向量化（Vectorization）编程思维。

目标：
1. 生成 M 种不同的随机权重组合
2. 用 for 循环和矩阵乘法分别计算这 M 个组合在 T 天的收益序列，并对比性能
3. 理解 R @ W.T 的维度转换魔法： (T, N) @ (N, M) -> (T, M)
4. 计算累计收益率（资金曲线），体会 cumprod 的用法
"""

# %% [0. 导入依赖库]
import numpy as np
import pandas as pd
import os
import time

print("✅ 依赖库导入完成")

# %% [1. 数据加载与预处理]
# 【复习】动态路径与读取面板数据
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
parquet_path = os.path.join(project_root, 'Database', 'files', 'panel_50stocks.parquet')

df_panel = pd.read_parquet(parquet_path)

# 选择 50 只股票参与回测
selected = df_panel['symbol'].unique()[:50]
N = len(selected)

# 转换为宽表
df_returns = df_panel[df_panel['symbol'].isin(selected)].pivot_table(
    index='trade_date',
    columns='symbol',
    values='daily_return'
).dropna()

# 截取最近的 252 个交易日（约一年）
df_returns = df_returns.tail(252)

R = df_returns.values  # 收益率矩阵，shape: (T, N)
T = R.shape[0]

print(f"收益率矩阵 R shape: {R.shape}  # ({T} 个交易日, {N} 只股票)")

# %% [2. 生成 M 种回测策略组合]
# 【编程概念】np.random.dirichlet
# 生成和为 1 的随机数，天然适合生成非负且满仓的投资组合权重
M = 10_000  # 模拟 1 万种不同的策略（组合）
np.random.seed(42)
W = np.random.dirichlet(np.ones(N), size=M)

print(f"策略权重矩阵 W shape: {W.shape}  # ({M} 个策略, {N} 只股票)")
print("W 的每一行代表一个策略在 N 只股票上的配置比例，且行和为 1。")

# %% [3. 性能对决：for 循环 vs 矩阵向量化计算]
# 【金融直觉】我们要计算每天每个策略的收益。
# 某天某策略收益 = sum(该天各股票收益 * 该策略各股票权重)
# 即向量点乘。

print("\n" + "=" * 50)
print("⏱️ 性能对决：1万个策略回测 252 天")
print("=" * 50)

# 方法 A：原生态双重 for 循环 (Pythonic 灾难)
t0 = time.perf_counter()
returns_loop = np.zeros((T, M))
for t in range(T):           # 遍历 252 天
    for m in range(M):       # 遍历 10000 个策略
        # R[t] 是第 t 天 N 只股票的收益，W[m] 是第 m 个策略的权重
        returns_loop[t, m] = np.dot(R[t], W[m])
time_loop = time.perf_counter() - t0

# 方法 B：纯矩阵乘法 (BLAS 并行加速)
# 【数学概念】
# R 的 shape 是 (T, N)
# W.T 的 shape 是 (N, M)
# R @ W.T 的结果 shape 是 (T, M)
# 正好就是 T 天里 M 个策略的每天收益率！没有一行 for 循环！
t0 = time.perf_counter()
returns_matrix = R @ W.T     # 核心就在这五个字符： R @ W.T
time_matrix = time.perf_counter() - t0

# 验证一致性
assert np.allclose(returns_loop, returns_matrix), "两种计算结果不一致！"

print(f"🐌 双重 for 循环耗时 : {time_loop * 1000:.1f} ms")
print(f"🚀 矩阵化 (R @ W.T) 耗时: {time_matrix * 1000:.1f} ms")
print(f"🔥 加速比 : {time_loop / time_matrix:.0f}x")
print("在量化回测框架（如 VectorBT 底层）中，消灭循环是极致性能的绝对核心。")

# %% [4. 计算资金净值曲线 (Cumulative Returns / NAV)]
# 【数学概念】
# 资金净值 NAV_t = NAV_{t-1} * (1 + R_t)
# 所以 T 天的净值序列 = 累积乘积 (Cumulative Product)
#
# 【编程概念】np.cumprod
# axis=0 表示沿着时间维度（行向下）累乘。
# 比如第一天是 (1+R1)，第二天是 (1+R1)*(1+R2)，以此类推。

print("\n" + "=" * 50)
print("📈 生成全量资金净值曲线")
print("=" * 50)

# 第一步：计算 1 + R
gross_returns = 1 + returns_matrix  # Broadcasting: 标量 1 加到 (T, M) 的每一个元素上

# 第二步：沿时间轴累乘
# shape: (T, M) -> (T, M)
nav_matrix = np.cumprod(gross_returns, axis=0)

print(f"净值矩阵 nav_matrix shape: {nav_matrix.shape}")
print(f"（包含 {nav_matrix.shape[1]} 个策略在 {nav_matrix.shape[0]} 天的完整资金曲线）")

# %% [5. 回测结果简单分析]
# 获取期末（最后一天）的净值，这就是一年的总收益（本金变为多少倍）
final_navs = nav_matrix[-1, :]  # shape: (M,)

# 找出表现最好和最差的策略
best_idx = np.argmax(final_navs)
worst_idx = np.argmin(final_navs)

best_return = (final_navs[best_idx] - 1) * 100
worst_return = (final_navs[worst_idx] - 1) * 100
mean_return = (final_navs.mean() - 1) * 100

print("\n📊 1 万种随机策略的一年期回测概览：")
print(f"  最高收益: {best_return:+.2f}%  (策略 #{best_idx})")
print(f"  最低收益: {worst_return:+.2f}%  (策略 #{worst_idx})")
print(f"  平均收益: {mean_return:+.2f}%")

print("\n最佳策略的权重配置预览（前 5 只股票）：")
for i, sym in enumerate(selected[:5]):
    weight = W[best_idx, i]
    print(f"  {sym}: {weight*100:.2f}%")

print("\n✅ Day 6 完成！一行代码搞定一万个策略的全量回测。")

# %%
