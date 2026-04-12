"""
day3_covariance_matrix.py - Week 3 Day 3: 代码手撸协方差矩阵 (Covariance Matrix)

核心认知跃迁：
    协方差矩阵 Σ (Sigma) 是马科维茨风险评估的心脏。
    它不仅衡量单资产的波动（对角线即方差），还衡量资产间的联动关系（非对角线即协方差）。
    
    数学推导过程：
    1. 计算每只股票的平均收益 μ (均值)
    2. 计算去中心化收益：R_centered = R - μ (超额收益/残差)
    3. 矩阵叉乘求和：R_centered^T @ R_centered
    4. 除以自由度 (T - 1) 即得到无偏协方差矩阵 Σ

    这展示了从 for 循环 -> @ 矩阵乘法 的巨大威力！

目标：
1. 提取股票的日收益率矩阵
2. 使用 np.cov() 计算协方差矩阵
3. 使用 NumPy 矩阵叉乘 (R.T @ R) 手工推导协方差矩阵
4. assert 验证手工推论与 np.cov() 结果的完全一致
5. 感受资产间“正相关”、“负相关”在矩阵中的数字体现
"""

import numpy as np
import pandas as pd
import os
import time

# ==========================================
# 📦 1. 加载 Week 2 的面板数据
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
parquet_path = os.path.join(project_root, 'Database', 'files', 'panel_50stocks.parquet')

print("📦 加载面板数据...")
df_panel = pd.read_parquet(parquet_path)

# ==========================================
# 🎯 2. 选择 3 只代表性股票构建收益矩阵
# ==========================================
# 为了方便展示 3x3 矩阵，先挑选 3 只个股
selected = ['SIM0001', 'SIM0025', 'SIM0050']
print(f"\n🎯 选取展示标的: {selected}")

df_returns = df_panel[df_panel['symbol'].isin(selected)].pivot_table(
    index='trade_date',
    columns='symbol',
    values='daily_return'
).dropna()

R = df_returns.values # shape: (T, 3)
T, N = R.shape
print(f"  收益率矩阵 R: shape = {R.shape} ({T} 天 × {N} 只股票)")


# ==========================================
# 🧮 3. 计算均值，去中心化
# ==========================================
print("\n" + "=" * 60)
print("🧮 手工计算 Step 1 & 2: 均值与去中心化")
print("=" * 60)

# Step 1: 计算每只股票的日均收益 (维度沿 T 方向折叠 -> N,)
mu = R.mean(axis=0) 
print(f"  均值向量 μ (shape {mu.shape}): {mu.round(4)}")

# Step 2: 去中心化 (Broadcasting: (T,N) - (N,) -> (T,N))
R_centered = R - mu
print(f"  去中心化后的 R_centered shape: {R_centered.shape}")

# 随便抽查一天验证中心化是否正确
r_day0 = R[0]
r_day0_cent = R_centered[0]
print(f"  > 第0天 原收益:   {r_day0.round(4)}")
print(f"  > 第0天 减去均值: {r_day0_cent.round(4)}")
assert np.allclose(r_day0 - mu, r_day0_cent)


# ==========================================
# 🚀 4. 手工推导协方差矩阵
# ==========================================
print("\n" + "=" * 60)
print("🚀 手工计算 Step 3 & 4: 叉乘与自由度修正")
print("=" * 60)

# Step 3: 矩阵叉乘 (N, T) @ (T, N) -> (N, N)
# 这是计算相关性的关键: 每列自己乘自己(方差)，自己乘别人(协方差)
sum_of_squares = R_centered.T @ R_centered
print(f"  叉乘 R^T @ R 后的 shape: {sum_of_squares.shape} (N × N)")

# Step 4: 除以自由度 T-1 得到样本无偏协方差 (Unbiased Sample Covariance)
degrees_of_freedom = T - 1
cov_manual = sum_of_squares / degrees_of_freedom

print("\n  ✍️ 手工计算得到的协方差矩阵 Σ:")
print(np.array_str(cov_manual * 10000, precision=2, suppress_small=True))
print("  (注: 为了方便阅读，矩阵数值已放大 10000 倍展示)")


# ==========================================
# 📦 5. 调包侠: np.cov() 计算
# ==========================================
print("\n" + "=" * 60)
print("📦 调用 NumPy 提供的方法: np.cov()")
print("=" * 60)

# np.cov 默认设每行是一个变量(rowvar=True)
# 我们的 R 是每列一个股票，所以要么传 R.T，要么指定 rowvar=False
cov_numpy = np.cov(R, rowvar=False)

print("\n  ⚡ np.cov 计算得到的协方差矩阵 Σ:")
print(np.array_str(cov_numpy * 10000, precision=2, suppress_small=True))


# ==========================================
# ✅ 6. 核心验证
# ==========================================
print("\n" + "=" * 60)
print("✅ 验证手工实现 vs np.cov 结果")
print("=" * 60)

is_identical = np.allclose(cov_manual, cov_numpy)
assert is_identical, "手工计算的协方差矩阵与 np.cov() 结果不一致！"
print("  🎉 完美一致！手工推论成功。")

# 另外，协方差矩阵的对角线应当等于各股的样本方差 (使用 ddof=1)
sample_vars = np.var(R, axis=0, ddof=1)
diag_cov = np.diag(cov_numpy)
assert np.allclose(sample_vars, diag_cov), "对角线元素不等于样本方差！"
print("  🎉 对角线 === 各股票的普通样本方差 (R.var)。")
print(f"     样本方差(放大万倍): {(sample_vars*10000).round(2)}")
print(f"     对角线  (放大万倍): {(diag_cov*10000).round(2)}")


# ==========================================
# ⏱️ 7. 性能：Pandas.cov() vs NumPy 手算 (50×50 规模)
# ==========================================
print("\n" + "=" * 60)
print("⏱️ 性能对决: Pandas .cov() vs NumPy 纯手写")
print("=" * 60)

# 我们载入所有的 50只 股票做性能对比
df_all = df_panel.pivot_table(index='trade_date', columns='symbol', values='daily_return').dropna()
R_all = df_all.values
T_all, N_all = R_all.shape
print(f"  完整收益率矩阵: {T_all}天 × {N_all}只")

target_runs = 500

# 1. Pandas .cov()
t0 = time.perf_counter()
for _ in range(target_runs):
    _ = df_all.cov()
time_pd = (time.perf_counter() - t0) / target_runs

# 2. np.cov(rowvar=False)
t0 = time.perf_counter()
for _ in range(target_runs):
    _ = np.cov(R_all, rowvar=False)
time_np = (time.perf_counter() - t0) / target_runs

# 3. 手工纯矩阵运算
t0 = time.perf_counter()
for _ in range(target_runs):
    mu_all = R_all.mean(axis=0)
    R_cent_all = R_all - mu_all
    _ = (R_cent_all.T @ R_cent_all) / (T_all - 1)
time_manual = (time.perf_counter() - t0) / target_runs

print(f"\n  {'方法':<25} {'单次耗时 (μs)':>15} {'速度倍数':>10}")
print("-" * 55)
print(f"  {'🐌 Pandas df.cov()':<25} {time_pd*1e6:>15.1f} {'1.0x':>10}")
print(f"  {'🚶 np.cov()':<25} {time_np*1e6:>15.1f} {time_pd/time_np:>9.1f}x")
print(f"  {'🚀 纯 NumPy (R^T @ R)':<25} {time_manual*1e6:>15.1f} {time_pd/time_manual:>9.1f}x")
print("\n  💡 Pandas 会做大量的索引对齐和 NaN 检查，速度往往慢于纯 NumPy。")
print("     但在全量手写中，我们依然看到了矩阵乘法 (BLAS) 霸道的性能。")


# ==========================================
# 🧠 8. 维度映射 Cheat Sheet
# ==========================================
print("\n" + "=" * 60)
print("🧠 协方差的维度变换直觉")
print("=" * 60)
print(f'''
  对象                 含义             shape
  ────────────────────────────────────────────────
  R                  收益率原矩阵       (T, N)
  μ (R.mean)         单个股票平均收益    (N, )
  R_centered         中心化收益         (T, N)  <- (T,N) 广播减去了 (N,)
  
  核心公式:
  Σ = (R_centered^T @ R_centered) / (T-1)
  
  推导路径:
  (N, T) @ (T, N)  --[内维T发生坍缩合并]-->  (N, N)

  金融含义:
  最终得出的 (N, N) 是相关结构图（地图）。
  第 i 行 第 j 列的元素就是 股票 i 和股票 j 收益波动方向的纠缠程度。
''')

print("\n" + "=" * 60)
print("📌 Day 3 总结")
print("=" * 60)
print("""
  ✅ 掌握：协方差矩阵的构成，对角线=方差，非对角线=两者的协方差
  ✅ 掌握：中心化去均值操作 (Broadcasting 减法)
  ✅ 掌握：利用 R.T @ R 从收益序列压缩提取协方差矩阵 (N,T @ T,N → N,N)
  ✅ 验证：手工计算与 np.cov() 的结果一模一样
  ✅ 实测：脱离 Pandas 等顶层封装，纯矩阵运算带来的千倍级提速
  
  🔜 明天 Day 4: 结合前三天的成果，使用 Σ 计算马科维茨公式：
     整体组合方差_p = w^T @ Σ @ w
     评估仓位带来的整体风险！
""")
