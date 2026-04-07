"""
day1_vector_dot_product.py - Week 3 Day 1: 向量点乘与组合收益率

核心认知跃迁：
    股票配置权重 w = [w1, w2, w3]  →  1×N 行向量
    每日收益率   r = [r1, r2, r3]  →  N×1 列向量
    组合收益率   R_p = w · r = w1*r1 + w2*r2 + w3*r3  → 标量

    这就是线性代数在量化里的第一个落地场景：
    一行 np.dot(w, r) 替代了 for 循环加权求和。

目标：
1. 从 Week 2 产出的 50 只股票面板数据中挑选 3 只
2. 定义权重向量，用 np.dot / @ 算出每日组合收益
3. 对比 for 循环 vs 向量化的速度差距
4. 可视化：单股 vs 组合 的净值曲线
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
print(f"  加载完成: {df_panel.shape[0]:,} 行 × {df_panel.shape[1]} 列")
print(f"  股票列表: {sorted(df_panel['symbol'].unique()[:5])}... 共 {df_panel['symbol'].nunique()} 只")

# ==========================================
# 🎯 2. 挑选 3 只股票，构建收益率矩阵
# ==========================================
# 选择 3 只不同风格的股票（稳健、中性、激进）
selected = ['SIM0001', 'SIM0025', 'SIM0050']
print(f"\n🎯 选取标的: {selected}")

# 将长表 pivot 为宽表：每列一只股票的日收益率
df_returns = df_panel[df_panel['symbol'].isin(selected)].pivot_table(
    index=df_panel.index.name if df_panel.index.name else 'trade_date',
    columns='symbol',
    values='daily_return'
)

# 确保索引是 trade_date
if df_returns.index.name != 'trade_date':
    # 面板数据可能以 trade_date 为索引
    pass

# 去掉 NaN（首行没有收益率）
df_returns = df_returns.dropna()
print(f"  收益率矩阵: {df_returns.shape[0]} 天 × {df_returns.shape[1]} 只")
print(f"  时间范围: {df_returns.index[0]} → {df_returns.index[-1]}")

# 看一眼收益率统计
print("\n📊 各股基本统计 (日度):")
stats = pd.DataFrame({
    '均值(bp)': (df_returns.mean() * 10000).round(2),
    '标准差(%)': (df_returns.std() * 100).round(3),
    '年化收益(%)': (((1 + df_returns.mean()) ** 252 - 1) * 100).round(2),
    '年化波动(%)': (df_returns.std() * np.sqrt(252) * 100).round(2)
})
print(stats)


# ==========================================
# 🧮 3. 核心：向量点乘计算组合收益率
# ==========================================
print("\n" + "=" * 60)
print("🧮 核心 - 向量点乘: w · r = 组合当日收益")
print("=" * 60)

# 定义权重向量 —— 等权 1/3
weights = np.array([1/3, 1/3, 1/3])
print(f"\n  权重向量 w = {weights}")
print(f"  权重之和 = {weights.sum():.6f}  (必须为 1.0)")

# 取某一天的收益率作为演示
sample_day = df_returns.iloc[100]
r = sample_day.values  # 转为 numpy 数组

print(f"\n  样本日期: {sample_day.name}")
print(f"  收益向量 r = {r}")

# ---- 方法 1: for 循环（菜鸟写法）----
portfolio_return_loop = 0.0
for i in range(len(weights)):
    portfolio_return_loop += weights[i] * r[i]

print(f"\n  🐌 for 循环结果:  {portfolio_return_loop:.8f}")

# ---- 方法 2: np.dot（向量化）----
portfolio_return_dot = np.dot(weights, r)
print(f"  ⚡ np.dot 结果:   {portfolio_return_dot:.8f}")

# ---- 方法 3: @ 运算符（Python 3.5+ 矩阵乘法语法糖）----
portfolio_return_at = weights @ r
print(f"  ⚡ w @ r 结果:    {portfolio_return_at:.8f}")

# 验证三种方法一致
assert np.isclose(portfolio_return_loop, portfolio_return_dot), "结果不一致！"
assert np.isclose(portfolio_return_dot, portfolio_return_at), "结果不一致！"
print(f"\n  ✅ 三种方法结果一致: {portfolio_return_at:.8f}")
print(f"  💡 含义: 当天持有这个组合，资产变化 {portfolio_return_at*100:.4f}%")


# ==========================================
# ⏱️ 4. 性能对决：循环 vs 向量化（全量时间序列）
# ==========================================
print("\n" + "=" * 60)
print("⏱️ 性能对决: 计算全部交易日的组合收益")
print("=" * 60)

# 收益率矩阵: T×N (交易日数 × 股票数)
R = df_returns.to_numpy()  # shape: (T, N)，保证是 np.ndarray
T, N = R.shape
print(f"\n  收益率矩阵 R: shape = {R.shape}")
print(f"  即 {T} 个交易日 × {N} 只股票")

# ---- 方法 A: 双重 for 循环 ----
t0 = time.perf_counter()
portfolio_returns_loop = np.zeros(T)
for t in range(T):
    daily_sum = 0.0
    for j in range(N):
        daily_sum += weights[j] * R[t, j]
    portfolio_returns_loop[t] = daily_sum
time_loop = time.perf_counter() - t0

# ---- 方法 B: 单层 for + np.dot ----
t0 = time.perf_counter()
portfolio_returns_dot = np.zeros(T)
for t in range(T):
    portfolio_returns_dot[t] = np.dot(weights, R[t])
time_dot_loop = time.perf_counter() - t0

# ---- 方法 C: 全矩阵向量化 R @ w ----
t0 = time.perf_counter()
portfolio_returns_vec = R @ weights  # (T, N) @ (N,) = (T,)
time_vec = time.perf_counter() - t0

# 验证
assert np.allclose(portfolio_returns_loop, portfolio_returns_vec), "循环 vs 向量化结果不一致！"
assert np.allclose(portfolio_returns_dot, portfolio_returns_vec), "dot循环 vs 向量化结果不一致！"

print(f"\n  🐌 双重 for 循环:   {time_loop*1000:.2f} ms")
print(f"  🚶 单层 for+dot:    {time_dot_loop*1000:.2f} ms")
print(f"  🚀 全矩阵 R @ w:   {time_vec*1000:.4f} ms")
print(f"\n  加速比: {time_loop/time_vec:.0f}x (矩阵 vs 双循环)")
print(f"  💡 这就是 NumPy 向量化的威力：底层是 C/Fortran BLAS 优化")


# ==========================================
# 📈 5. 构建净值曲线 (NAV Curve)
# ==========================================
print("\n" + "=" * 60)
print("📈 净值曲线: 单股 vs 等权组合")
print("=" * 60)

# 组合净值 = cumprod(1 + 简单收益率) —— 从1开始
portfolio_nav = np.cumprod(1 + portfolio_returns_vec)

# 各单股净值
single_navs = {}
for col in selected:
    single_navs[col] = np.cumprod(1 + df_returns[col].values)

# 构建 DataFrame
df_nav = pd.DataFrame(index=df_returns.index)
for col in selected:
    df_nav[col] = single_navs[col]
df_nav['Portfolio'] = portfolio_nav

print("\n净值曲线（起点=1.0，终点值即累计收益倍数）:")
print(f"  {'标的':<12} {'终点净值':>10} {'年化收益%':>10} {'最大回撤%':>10}")
print(f"  {'-'*42}")
for col in df_nav.columns:
    nav = df_nav[col].values
    total_years = len(nav) / 252
    ann_ret = (nav[-1] ** (1/total_years) - 1) * 100
    max_dd = ((nav / np.maximum.accumulate(nav)) - 1).min() * 100
    print(f"  {col:<12} {nav[-1]:>10.4f} {ann_ret:>10.2f} {max_dd:>10.2f}")


# ==========================================
# 🔍 6. 不同权重方案对比
# ==========================================
print("\n" + "=" * 60)
print("🔍 权重敏感性: 不同配置方案的效果")
print("=" * 60)

weight_schemes = {
    '等权 (1/3, 1/3, 1/3)': np.array([1/3, 1/3, 1/3]),
    '偏重首只 (0.6, 0.2, 0.2)': np.array([0.6, 0.2, 0.2]),
    '偏重末只 (0.2, 0.2, 0.6)': np.array([0.2, 0.2, 0.6]),
    '仅首只 (1.0, 0, 0)': np.array([1.0, 0.0, 0.0]),
    '反向均衡 (0.5, 0.3, 0.2)': np.array([0.5, 0.3, 0.2]),
}

print(f"\n  {'方案':<28} {'终点净值':>10} {'年化收益%':>10} {'年化波动%':>10} {'夏普比':>8}")
print(f"  {'-'*66}")

for name, w in weight_schemes.items():
    assert np.isclose(w.sum(), 1.0), f"权重之和不为1: {w.sum()}"

    # 一行搞定：R @ w
    port_ret = R @ w
    nav = np.cumprod(1 + port_ret)
    total_years = len(nav) / 252
    ann_ret = (nav[-1] ** (1/total_years) - 1) * 100
    ann_vol = port_ret.std() * np.sqrt(252) * 100
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0

    print(f"  {name:<28} {nav[-1]:>10.4f} {ann_ret:>10.2f} {ann_vol:>10.2f} {sharpe:>8.3f}")

print(f"\n  💡 关键发现: 权重向量 w 是投资者唯一能控制的变量")
print("     后续 Week 3 Day 4 将用马科维茨优化来寻找'最优 w'")


# ==========================================
# 🧠 7. 概念加固：维度与 shape 的直觉
# ==========================================
print("\n" + "=" * 60)
print("🧠 维度直觉 Cheat Sheet")
print("=" * 60)

print(f"""
  对象              含义                    NumPy shape
  ─────────────────────────────────────────────────────
  w (权重)          投资者的"旋钮"          ({N},)  或 (1, {N})
  r_t (单日收益)    市场当天的"随机信号"    ({N},)
  R (收益率矩阵)    所有历史信号堆叠        ({T}, {N})
  
  运算                  代码              结果 shape
  ─────────────────────────────────────────────────────
  单日组合收益      w @ r_t              标量 ()
  全量组合收益      R @ w                ({T},)
  组合方差(预告)    w @ Σ @ w            标量 () ← Day 4

  核心公式:
    R_p(t) = Σ w_i · r_i(t) = w^T · r(t) = w @ r_t
    
  金融含义:
    每天，你把各股收益按照仓位权重加权求和，
    得到的就是你组合的真实 PnL（盈亏）。
""")


# ==========================================
# ✅ 8. 自测断言
# ==========================================
print("✅ 运行自测断言...")

# 断言 1: 权重之和为 1
w_test = np.array([0.4, 0.35, 0.25])
assert np.isclose(w_test.sum(), 1.0)

# 断言 2: np.dot 与 @ 等价
r_test = np.array([0.01, -0.02, 0.03])
assert np.isclose(np.dot(w_test, r_test), w_test @ r_test)

# 断言 3: 矩阵乘法维度正确
R_test = np.random.randn(10, 3)
result = R_test @ w_test
assert result.shape == (10,), f"期望 (10,) 但得到 {result.shape}"

# 断言 4: 等权组合收益 = 各股收益的算术平均
w_equal = np.ones(3) / 3
r_check = np.array([0.03, -0.01, 0.02])
assert np.isclose(w_equal @ r_check, r_check.mean())

print("  全部通过 ✅")

print(f"\n{'='*60}")
print("📌 Day 1 总结")
print(f"{'='*60}")
print("""
  ✅ 掌握：np.dot(w, r) 和 w @ r 计算加权组合收益
  ✅ 理解：权重向量 w 是 1×N，收益向量 r 是 N×1，点乘得标量
  ✅ 实战：R @ w 一行代码算出全量交易日的组合PnL序列
  ✅ 对比：向量化 vs for 循环的性能差距（通常 100x+）
  ✅ 发现：不同权重方案下组合表现差异巨大
  
  🔜 明天 Day 2: 元素乘法(*) vs 矩阵乘法(@) 的本质区别
     + 50天×50只 大规模矩阵运算性能对比
""")
