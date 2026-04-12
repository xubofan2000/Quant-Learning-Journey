"""
day2_elementwise_vs_matmul.py - Week 3 Day 2: 按元素乘法(*) vs 矩阵叉乘(@)

核心认知跃迁：
    * 运算符：逐元素相乘（Element-wise Multiply）
      shape 相同 → 对应位置相乘，结果 shape 不变
      例：[0.5, 0.3, 0.2] * [0.01, -0.02, 0.03] = [0.005, -0.006, 0.006]

    @ 运算符：矩阵乘法（Matrix Multiply / Dot Product）
      内维必须匹配 → 结果"坍缩"为更小的 shape
      例：w @ r = 0.5*0.01 + 0.3*(-0.02) + 0.2*0.03 = 0.005  → 标量

    金融直觉：
      * → "每只股票各自贡献了多少收益"（分项明细）
      @ → "把所有贡献加总为组合总收益"（汇总数字）
      w * r 然后 sum()  ==  w @ r

    Pandas 底层剥开就是 NumPy：
      df.values / df.to_numpy() 拿到的就是 np.ndarray
      DataFrame 的算术运算本质上调的就是 NumPy 的广播与矩阵运算

目标：
1. 加载 50 只股票面板数据，构建 50天×50只 的收益矩阵
2. 对比 * (element-wise) 与 @ (matrix multiply) 的行为差异
3. 理解 broadcasting 的展开机制
4. for 循环 vs NumPy 矩阵运算求和的性能对决（50×50 规模）
5. 揭示 Pandas → NumPy 的底层映射关系
"""

import numpy as np
import pandas as pd
import os
import time

# ==========================================
# 📦 1. 加载 50 只股票面板数据
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
parquet_path = os.path.join(project_root, 'Database', 'files', 'panel_50stocks.parquet')

print("📦 加载面板数据...")
df_panel = pd.read_parquet(parquet_path)
n_stocks = df_panel['symbol'].nunique()
n_days = len(df_panel) // n_stocks
print(f"  加载完成: {df_panel.shape[0]:,} 行 × {df_panel.shape[1]} 列")
print(f"  股票数: {n_stocks}, 交易日数(约): {n_days}")


# ==========================================
# 🎯 2. 构建收益率矩阵：50天 × 50只股票
# ==========================================
print("\n" + "=" * 60)
print("🎯 构建收益率矩阵 R (50天 × 50只股票)")
print("=" * 60)

# 将长表 pivot 为宽表：index=日期, columns=股票代码, values=日收益率
all_symbols = sorted(df_panel['symbol'].unique())
df_wide = df_panel.pivot_table(
    index='trade_date',
    columns='symbol',
    values='daily_return'
)

# 去掉 NaN 行（首行无收益率）
df_wide = df_wide.dropna()
total_days = len(df_wide)

# 截取最近 50 个交易日（方便展示和性能对比）
SLICE_DAYS = 50
df_slice = df_wide.tail(SLICE_DAYS)
print(f"\n  截取最近 {SLICE_DAYS} 个交易日")
print(f"  收益率矩阵 shape: {df_slice.shape}")
print(f"  即 {df_slice.shape[0]} 天 × {df_slice.shape[1]} 只股票")

# 转为 NumPy 数组
R = df_slice.to_numpy()  # shape: (50, 50)
T, N = R.shape
print(f"  R.shape = ({T}, {N})")
print(f"  数据类型: {R.dtype}")


# ==========================================
# 🔬 3. 核心实验：* vs @ 的本质区别
# ==========================================
print("\n" + "=" * 60)
print("🔬 核心实验: * (逐元素) vs @ (矩阵乘法)")
print("=" * 60)

# 定义等权权重向量
weights = np.ones(N) / N  # 50只股票各占 2%

# 取第一天做演示
r_day0 = R[0]  # shape: (50,)

print(f"\n  权重向量 w: shape = {weights.shape}, 前5个 = {weights[:5]}")
print(f"  收益向量 r: shape = {r_day0.shape}, 前5个 = {r_day0[:5].round(4)}")

# ---- 实验 A: 逐元素乘法 * ----
elementwise = weights * r_day0
print(f"\n  📌 w * r (逐元素乘法):")
print(f"     shape = {elementwise.shape}")
print(f"     前5个 = {elementwise[:5].round(6)}")
print(f"     含义: 每只股票对组合收益的贡献值（未求和）")

# ---- 实验 B: 手动求和 sum(*) ----
manual_portfolio = np.sum(elementwise)
print(f"\n  📌 sum(w * r):")
print(f"     结果 = {manual_portfolio:.8f}")
print(f"     含义: 把每只股票的贡献加起来 = 组合总收益")

# ---- 实验 C: 矩阵乘法 @ ----
matmul_portfolio = weights @ r_day0
print(f"\n  📌 w @ r (矩阵乘法):")
print(f"     结果 = {matmul_portfolio:.8f}")
print(f"     含义: 一步到位 = 加权求和 = 组合总收益")

# 验证等价
assert np.isclose(manual_portfolio, matmul_portfolio), "sum(w*r) != w@r !"
print(f"\n  ✅ sum(w * r) == w @ r  →  两者等价!")
print(f"     但 @ 是一步到位，* + sum() 是两步拆解")

print(f"""
  🧠 直觉对照:
  ──────────────────────────────────────────────────
  运算符     作用             shape 变化       金融含义
  ──────────────────────────────────────────────────
  w * r      逐位相乘         (N,) → (N,)     每只股票的收益贡献明细
  sum(w * r) 求和             (N,) → 标量      贡献汇总 = 组合收益
  w @ r      内积(一步到位)   (N,) → 标量      组合收益(直接结果)
  ──────────────────────────────────────────────────

  💡 本质: @ = * + sum()
     但 @ 底层调用 BLAS 的 dot 产品，比先 * 再 sum() 更快更高效
""")


# ==========================================
# 🌊 4. Broadcasting：不同 shape 的 * 会发生什么？
# ==========================================
print("=" * 60)
print("🌊 Broadcasting: 不同 shape 逐元素相乘的自动展开")
print("=" * 60)

# 场景：50天 × 50只 的收益矩阵 R，与 50只 的权重向量 w
print(f"\n  R shape = {R.shape}  ({T}天 × {N}只)")
print(f"  w shape = {weights.shape}  (权重向量)")

# Broadcasting: (50, 50) * (50,) → (50, 50)
# NumPy 自动将 w 从 (50,) 扩展为 (1, 50)，再逐行复制为 (50, 50)
contribution_matrix = R * weights  # broadcasting!
print(f"\n  R * w (broadcasting):")
print(f"    结果 shape = {contribution_matrix.shape}")
print(f"    含义: 每一行 = 某天每只股票的收益贡献值")

# 按行求和 = 每天的组合收益
daily_portfolio_returns = contribution_matrix.sum(axis=1)  # shape: (50,)
print(f"    sum(axis=1) shape = {daily_portfolio_returns.shape}")
print(f"    含义: 每天的组合收益序列")

# 对比：直接用 @
matmul_daily = R @ weights  # shape: (50,)
assert np.allclose(daily_portfolio_returns, matmul_daily), "broadcasting结果不一致!"
print(f"\n  ✅ (R * w).sum(axis=1) == R @ w  →  等价!")

# 再对比另一种写法
alt = np.einsum('ij,j->i', R, weights)  # Einstein summation
assert np.allclose(alt, matmul_daily), "einsum结果不一致!"
print(f"  ✅ np.einsum('ij,j->i', R, w) == R @ w  →  也等价!")

print(f"""
  🧠 Broadcasting 展开图示:
  ──────────────────────────────────────────────────
  R  (50, 50)     w  (50,)           R * w  (50, 50)
  ┌──────────┐    ┌──────┐          ┌──────────────┐
  │ r₁₁ r₁₂ │    │ w₁ w₂│   →      │ r₁₁w₁ r₁₂w₂ │
  │ r₂₁ r₂₂ │  * │ ...  │          │ r₂₁w₁ r₂₂w₂ │
  │  ...     │    │ w₅₀  │          │  ...         │
  └──────────┘    └──────┘          └──────────────┘
                  ↑ 自动复制50行
  ──────────────────────────────────────────────────

  💡 * 是 broadcasting（扩张），@ 是 contraction（坍缩）
     * : (T,N) * (N,) → (T,N)   维度不变，信息展开
     @ : (T,N) @ (N,) → (T,)    内维消融，信息压缩
""")


# ==========================================
# ⏱️ 5. 性能对决：for 循环 vs NumPy（50×50 规模）
# ==========================================
print("=" * 60)
print("⏱️ 性能对决: 计算全量 50天×50只 的组合收益序列")
print("=" * 60)

REPEAT = 1000  # 多次运行取平均，放大时间差异

# ---- 方法 A: 双重 for 循环 ----
t0 = time.perf_counter()
for _ in range(REPEAT):
    result_loop = np.zeros(T)
    for t in range(T):
        daily_sum = 0.0
        for j in range(N):
            daily_sum += weights[j] * R[t, j]
        result_loop[t] = daily_sum
time_loop = (time.perf_counter() - t0) / REPEAT

# ---- 方法 B: 单层 for + 手动累加 ----
t0 = time.perf_counter()
for _ in range(REPEAT):
    result_single = np.zeros(T)
    for t in range(T):
        result_single[t] = np.sum(weights * R[t])  # * + sum
time_single = (time.perf_counter() - t0) / REPEAT

# ---- 方法 C: broadcasting: (R * w).sum(axis=1) ----
t0 = time.perf_counter()
for _ in range(REPEAT):
    result_broadcast = (R * weights).sum(axis=1)
time_broadcast = (time.perf_counter() - t0) / REPEAT

# ---- 方法 D: 矩阵乘法 R @ w ----
t0 = time.perf_counter()
for _ in range(REPEAT):
    result_matmul = R @ weights
time_matmul = (time.perf_counter() - t0) / REPEAT

# ---- 方法 E: einsum ----
t0 = time.perf_counter()
for _ in range(REPEAT):
    result_einsum = np.einsum('ij,j->i', R, weights)
time_einsum = (time.perf_counter() - t0) / REPEAT

# 验证所有方法结果一致
assert np.allclose(result_loop, result_matmul), "双重循环结果不一致!"
assert np.allclose(result_single, result_matmul), "单层循环结果不一致!"
assert np.allclose(result_broadcast, result_matmul), "broadcasting结果不一致!"
assert np.allclose(result_einsum, result_matmul), "einsum结果不一致!"

print(f"\n  矩阵规模: {T}天 × {N}只, 重复 {REPEAT} 次取平均\n")
print(f"  {'方法':<30} {'单次耗时':>12} {'相对速度':>10}")
print(f"  {'-'*52}")
print(f"  {'🐌 双重 for 循环':<30} {time_loop*1e6:>10.1f} μs {'1.0x':>10}")
print(f"  {'🚶 单层 for + sum(w*r)':<30} {time_single*1e6:>10.1f} μs {time_loop/time_single:>9.1f}x")
print(f"  {'🔄 (R * w).sum(axis=1)':<30} {time_broadcast*1e6:>10.1f} μs {time_loop/time_broadcast:>9.1f}x")
print(f"  {'🚀 R @ w (矩阵乘法)':<30} {time_matmul*1e6:>10.1f} μs {time_loop/time_matmul:>9.1f}x")
print(f"  {'🎯 np.einsum':<30} {time_einsum*1e6:>10.1f} μs {time_loop/time_einsum:>9.1f}x")

print(f"\n  💡 结论:")
print(f"     - @ (矩阵乘法) 是最优解: 一步到位，BLAS 底层优化")
print(f"     - * + sum() 等价但多了一步，稍慢")
print(f"     - for 循环在 Python 层逐元素操作，解释器开销巨大")
print(f"     - 规模越大（N=500/5000），差距越夸张")


# ==========================================
# 🐼 6. Pandas 底层剥开就是 NumPy
# ==========================================
print("\n" + "=" * 60)
print("🐼 揭秘: Pandas 运算底层就是 NumPy")
print("=" * 60)

# 用 Pandas DataFrame 做同样的操作
df_w = pd.DataFrame(weights.reshape(1, -1), columns=df_slice.columns)  # 1行×50列
print(f"\n  df_slice (Pandas): shape = {df_slice.shape}, type = {type(df_slice)}")

# Pandas 的 * 和 @
pandas_elementwise = df_slice * df_w.iloc[0]  # broadcasting 逐元素
print(f"  df_slice * w:  shape = {pandas_elementwise.shape}")
print(f"    → 和 NumPy 的 R * w 完全一样!")

pandas_matmul_result = df_slice @ weights
print(f"  df_slice @ w:  shape = {pandas_matmul_result.shape}")

# 验证 Pandas 结果与 NumPy 一致
assert np.allclose(pandas_elementwise.sum(axis=1).values, result_matmul), "Pandas * 不一致!"
assert np.allclose(pandas_matmul_result.values, result_matmul), "Pandas @ 不一致!"
print(f"\n  ✅ Pandas 的 * 和 @ 结果与 NumPy 完全一致!")

# 底层验证: .to_numpy() / .values 拿到的是同一块内存
arr_from_values = df_slice.values
arr_from_to_numpy = df_slice.to_numpy()
print(f"\n  df_slice.values     类型: {type(arr_from_values)}")
print(f"  df_slice.to_numpy() 类型: {type(arr_from_to_numpy)}")
print(f"  两者是同一个对象? {arr_from_values is arr_from_to_numpy}")

# Pandas 的运算时间对比
t0 = time.perf_counter()
for _ in range(REPEAT):
    _ = df_slice @ weights
time_pandas_matmul = (time.perf_counter() - t0) / REPEAT

t0 = time.perf_counter()
for _ in range(REPEAT):
    _ = df_slice.values @ weights
time_numpy_from_pandas = (time.perf_counter() - t0) / REPEAT

print(f"\n  Pandas df @ w:     {time_pandas_matmul*1e6:.1f} μs")
print(f"  NumPy arr @ w:     {time_numpy_from_pandas*1e6:.1f} μs")
print(f"  开销比: {time_pandas_matmul/time_numpy_from_pandas:.2f}x")
print(f"  💡 Pandas 的 @ 底层调的还是 NumPy，但多了索引对齐的开销")


# ==========================================
# 🧪 7. 易错点实战：* 和 @ 的典型误用
# ==========================================
print("\n" + "=" * 60)
print("🧪 易错点: * 和 @ 的典型误用场景")
print("=" * 60)

# 误用 1: 想算组合收益但用了 *
r_example = np.array([0.01, -0.02, 0.03])
w_example = np.array([0.5, 0.3, 0.2])

wrong = w_example * r_example  # 这不是组合收益!
correct = w_example @ r_example

print(f"\n  ⚠️ 误用1: 想'组合收益'却用了 *")
print(f"    w * r   = {wrong}")
print(f"    w @ r   = {correct:.6f}")
print(f"    * 给的是明细数组，@ 给的是总和标量")
print(f"    若忘了 sum()，你会拿错数据!")

# 误用 2: 维度不匹配时的 @ 会报错
print(f"\n  ⚠️ 误用2: 维度不匹配时 @ 直接报错")
try:
    bad = R @ R  # (50, 50) @ (50, 50) → (50, 50)，虽然不报错但含义全错!
    print(f"    R @ R 居然不报错! shape = {bad.shape}")
    print(f"    但金融含义完全不对: 这是矩阵×矩阵，不是组合收益!")
except ValueError as e:
    print(f"    报错: {e}")

# 正确的 R @ R 是什么含义？
print(f"\n  📌 (T,N) @ (N,T) = (T,T) → 每两天之间的收益协方差关系")
print(f"     R @ R.T 的 shape = {(R @ R.T).shape}")
print(f"     这其实就是未中心化的协方差矩阵（预告 Day 3）")

# 误用 3: * 做矩阵乘法的维度陷阱
print(f"\n  ⚠️ 误用3: (T,N) * (T,N) 逐元素 — 不是矩阵乘法!")
element_R = R * R  # 逐元素平方
print(f"    R * R shape = {element_R.shape}")
print(f"    含义: 每个收益率的平方（方差计算的中间步骤）")
print(f"    这 ≠ R @ R.T（协方差结构）")


# ==========================================
# 📊 8. 综合实战：50只股票组合分析
# ==========================================
print("\n" + "=" * 60)
print("📊 综合实战: 50只等权组合 — 用 @ 一步到位")
print("=" * 60)

# 全量数据（不截取50天，用全部）
R_full = df_wide.dropna().to_numpy()
T_full, N_full = R_full.shape
w_full = np.ones(N_full) / N_full

print(f"\n  全量矩阵: {T_full}天 × {N_full}只")

# 一步计算组合收益序列
portfolio_returns_full = R_full @ w_full

# 组合净值
portfolio_nav_full = np.cumprod(1 + portfolio_returns_full)

# 统计
ann_ret = ((portfolio_nav_full[-1] ** (252 / T_full)) - 1) * 100
ann_vol = portfolio_returns_full.std() * np.sqrt(252) * 100
sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
max_dd = ((portfolio_nav_full / np.maximum.accumulate(portfolio_nav_full)) - 1).min() * 100

print(f"\n  📈 50只等权组合表现:")
print(f"     年化收益:   {ann_ret:>8.2f}%")
print(f"     年化波动:   {ann_vol:>8.2f}%")
print(f"     夏普比率:   {sharpe:>8.3f}")
print(f"     最大回撤:   {max_dd:>8.2f}%")
print(f"     终点净值:   {portfolio_nav_full[-1]:>8.4f}")

# 对比：单只股票 vs 组合 的波动率
single_vols = df_wide.std() * np.sqrt(252) * 100
print(f"\n  📊 波动率对比:")
print(f"     单只股票平均年化波动: {single_vols.mean():.2f}%")
print(f"     等权组合年化波动:     {ann_vol:.2f}%")
print(f"     分散化效应: 降低了 {single_vols.mean() - ann_vol:.2f}% (约 {(1 - ann_vol/single_vols.mean())*100:.1f}%)")
print(f"     💡 这就是分散化投资(Diversification)的数学证明!")


# ==========================================
# 🧠 9. Cheat Sheet: * vs @ 全景对照
# ==========================================
print("\n" + "=" * 60)
print("🧠 Cheat Sheet: * vs @ 全景对照")
print("=" * 60)

print(f"""
  ┌─────────────┬──────────────────────┬──────────────────────┐
  │             │   * 逐元素乘法        │   @ 矩阵乘法         │
  ├─────────────┼──────────────────────┼──────────────────────┤
  │ 别名        │  Hadamard 积         │  内积 / 点积         │
  │ 维度规则    │  相同 shape 或可广播  │  内维必须匹配        │
  │ 结果 shape  │  不变(或广播扩展)    │  内维坍缩            │
  │ 数学记号    │  A ⊙ B              │  A · B  /  A^T B    │
  │ 金融含义    │  逐项贡献明细        │  加权汇总/总收益     │
  │ 性能        │  内存开销大(展开)    │  BLAS 优化(压缩)     │
  ├─────────────┼──────────────────────┼──────────────────────┤
  │ w * r       │  (N,) → (N,)         │  N/A                 │
  │ w @ r       │  N/A                 │  (N,) → 标量         │
  │ R * w       │  (T,N) → (T,N)      │  N/A                 │
  │ R @ w       │  N/A                 │  (T,N) → (T,)        │
  │ R * R       │  (T,N) → (T,N)      │  N/A                 │
  │ R @ R.T     │  N/A                 │  (T,N)(N,T) → (T,T)  │
  └─────────────┴──────────────────────┴──────────────────────┘

  核心记忆口诀:
    * 是"展开"（broadcasting）— 维度不变或增大
    @ 是"压缩"（contraction）— 内维消融，维度减小

  金融操作映射:
    算贡献明细 → w * r       (每只股票贡献了多少)
    算组合总收益 → w @ r     (所有贡献加总)
    算收益平方 → R * R       (方差的分子)
    算协方差结构 → R @ R.T   (Day 3 预告!)
""")


# ==========================================
# ✅ 10. 自测断言
# ==========================================
print("✅ 运行自测断言...")

# 断言 1: * + sum() == @
w_t = np.array([0.4, 0.35, 0.25])
r_t = np.array([0.01, -0.02, 0.03])
assert np.isclose(np.sum(w_t * r_t), w_t @ r_t), "* + sum != @"

# 断言 2: * 不改变 shape
result_star = w_t * r_t
assert result_star.shape == (3,), f"* 后 shape 应为 (3,), 实际 {result_star.shape}"

# 断言 3: @ 坍缩为标量
result_at = w_t @ r_t
assert result_at.shape == (), f"@ 后应为标量, 实际 shape {result_at.shape}"

# 断言 4: 矩阵 @ 向量 坍缩内维
R_t = np.random.randn(50, 50)
w_50 = np.ones(50) / 50
result_mat = R_t @ w_50
assert result_mat.shape == (50,), f"(50,50)@(50,) 应得 (50,), 实际 {result_mat.shape}"

# 断言 5: broadcasting (T,N) * (N,) == (T,N)
contrib = R_t * w_50
assert contrib.shape == (50, 50), f"broadcasting 后应为 (50,50), 实际 {contrib.shape}"

# 断言 6: broadcasting 的逐行结果等价于逐行 @
for i in range(5):  # 抽查前5行
    assert np.allclose(contrib[i].sum(), result_mat[i]), f"第{i}行不一致"

# 断言 7: 等权 * 等价于 mean
r_check = np.array([0.03, -0.01, 0.02])
w_equal = np.ones(3) / 3
assert np.isclose(w_equal @ r_check, r_check.mean()), "等权@ != mean"
assert np.isclose(np.sum(w_equal * r_check), r_check.mean()), "等权*+sum != mean"

print("  全部通过 ✅")


# ==========================================
# 📌 Day 2 总结
# ==========================================
print(f"\n{'='*60}")
print("📌 Day 2 总结")
print(f"{'='*60}")
print("""
  ✅ 掌握：* 是逐元素乘法(Hadamard积)，@ 是矩阵乘法(内积)
  ✅ 理解：* + sum() == @，但 @ 一步到位且底层 BLAS 优化更快
  ✅ 认知：* 是 broadcasting(展开)，@ 是 contraction(坍缩)
  ✅ 实战：50天×50只规模下，矩阵乘法比双重循环快数十到百倍
  ✅ 揭秘：Pandas 的 * 和 @ 底层调的就是 NumPy，多了索引对齐开销
  ✅ 发现：分散化效应的数学证明 — 等权组合波动率 < 单股平均波动率
  ✅ 警惕：R @ R 虽然不报错但含义全错，正确是 R @ R.T(协方差)

  🔜 明天 Day 3: 手撸协方差矩阵
     R @ R.T → 去均值 → 除以 T-1 → 协方差矩阵 Σ
     手工推导 vs np.cov() 的 assert 验证
""")
