"""
day4_portfolio_variance.py - Week 3 Day 4: 马科维茨组合方差 w^T @ Σ @ w

核心认知跃迁：
    有了协方差矩阵 Σ，我们终于可以"精确测量"任意权重组合的整体风险。

    马科维茨公式：
        σ²_p = w^T @ Σ @ w

    推导路径：
        w: (N,)    ← 权重行向量（投资者可控的唯一旋钮）
        Σ: (N, N)  ← 协方差矩阵（昨天 Day 3 手撸出来的）
        
        Σ @ w     : (N, N) @ (N,) → (N,)   第一步：矩阵向量积
        w @ (Σ@w) : (N,) · (N,)  → 标量    第二步：点乘 → 组合方差

    为什么不直接用收益序列的 std()?
        R @ w 算出的是每日组合收益时间序列 → 可以 .std() 得到历史波动率
        但马科维茨框架用 Σ 是解析公式，方便优化——不需要模拟路径！
        两者结果应该完全一致（当 Σ 用同一段历史数据估计时）。

目标：
1. 从 Σ 出发，用 w^T @ Σ @ w 计算组合方差
2. 验证 "解析方差" == "历史序列方差"（双重验证）
3. 遍历随机权重，描绘 风险-收益 散点图（简化有效前沿）
4. 找出等权 / 最小方差 / 最高夏普 三种典型组合并对比
"""

import numpy as np
import pandas as pd
import os
import time

# ==========================================
# 📦 1. 加载数据 & 构建 Σ（和 Day 3 完全相同）
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
parquet_path = os.path.join(project_root, 'Database', 'files', 'panel_50stocks.parquet')

print("📦 加载面板数据...")
df_panel = pd.read_parquet(parquet_path)

# 选 5 只股票，比 Day 3 的 3 只多一点，方便展示组合多样性
selected = ['SIM0001', 'SIM0010', 'SIM0020', 'SIM0035', 'SIM0050']
N = len(selected)
print(f"\n🎯 选取标的 ({N} 只): {selected}")

df_returns = df_panel[df_panel['symbol'].isin(selected)].pivot_table(
    index='trade_date',
    columns='symbol',
    values='daily_return'
).dropna()

R = df_returns.values  # shape: (T, N)
T, N = R.shape
print(f"  收益率矩阵 R: shape = {R.shape} ({T} 天 × {N} 只股票)")


# ==========================================
# 🧮 2. 构建协方差矩阵 Σ（手撸，复习 Day 3）
# ==========================================
print("\n" + "=" * 60)
print("🧮 构建协方差矩阵 Σ（Day 3 方法复习）")
print("=" * 60)

mu = R.mean(axis=0)                      # (N,)
R_centered = R - mu                      # (T, N)
Sigma = (R_centered.T @ R_centered) / (T - 1)  # (N, N)

print(f"  μ 均值向量 shape: {mu.shape}")
print(f"  Σ 协方差矩阵 shape: {Sigma.shape}")
print("\n  Σ 矩阵（放大万倍，方便阅读）:")
print(np.array_str(Sigma * 10_000, precision=2, suppress_small=True))

# 验证对角线 = 各股样本方差
assert np.allclose(np.diag(Sigma), np.var(R, axis=0, ddof=1)), "对角线应等于样本方差！"
print("\n  ✅ 对角线 == 样本方差，Σ 构建正确。")


# ==========================================
# 🚀 3. 核心：w^T @ Σ @ w 组合方差
# ==========================================
print("\n" + "=" * 60)
print("🚀 马科维茨公式: σ²_p = w^T @ Σ @ w")
print("=" * 60)

# 先用等权权重演示
w_equal = np.ones(N) / N
print(f"\n  权重向量 w (等权): {w_equal.round(4)}")

# 步骤拆解 ——————————————————————————
print("\n  — 步骤拆解 —")

# Step 1: Σ @ w  →  (N,)
step1 = Sigma @ w_equal
print(f"  Step 1  Σ @ w  shape: {step1.shape}")
print(f"          Σ @ w 值 (×10000): {(step1 * 10_000).round(4)}")

# Step 2: w^T · (Σ@w)  → 标量
var_p = w_equal @ step1          # 等价 w^T @ Sigma @ w
print(f"\n  Step 2  w^T · (Σ@w)  →  σ²_p = {var_p:.8f}")
sigma_p = np.sqrt(var_p)
print(f"          σ_p (日度波动率) = {sigma_p*100:.4f}%")
print(f"          σ_p (年化波动率) = {sigma_p * np.sqrt(252) * 100:.2f}%")

# — 双重验证：和历史序列直接 std 对比 ——————
portfolio_ret_series = R @ w_equal          # (T,)
sigma_p_historical = portfolio_ret_series.std(ddof=1)

print(f"\n  【验证】历史序列 std (ddof=1) = {sigma_p_historical * 100:.4f}%")
print(f"  【验证】w^T@Σ@w 开方           = {sigma_p * 100:.4f}%")
assert np.isclose(sigma_p, sigma_p_historical, rtol=1e-8), "两种方法结果不一致！"
print("  ✅ 完美一致！解析公式 == 历史序列实证")


# ==========================================
# ⏱️ 4. 性能：串行 for 循环 vs 批量矩阵运算
# ==========================================
print("\n" + "=" * 60)
print("⏱️ 性能对决：逐个 w 计算 vs 批量矩阵化")
print("=" * 60)

np.random.seed(42)
M = 50_000   # 测试组合数量

# 生成 M 个合法权重（Dirichlet 分布 → 自动满足非负且和为1）
W_all = np.random.dirichlet(np.ones(N), size=M)  # (M, N)
print(f"\n  生成 {M:,} 个随机权重组合（Dirichlet 分布）")

# —— 方法 A: Python for 循环 ——
t0 = time.perf_counter()
vars_loop = np.empty(M)
for i in range(M):
    vars_loop[i] = W_all[i] @ Sigma @ W_all[i]
time_loop = time.perf_counter() - t0

# —— 方法 B: 全矩阵化 (W_all @ Sigma) * W_all 求和 ——
# 利用: (M,N) @ (N,N) → (M,N); 再逐行与 W_all 点乘 → (M,)
t0 = time.perf_counter()
WS = W_all @ Sigma                       # (M, N)
vars_matrix = (WS * W_all).sum(axis=1)  # (M,)
time_matrix = time.perf_counter() - t0

assert np.allclose(vars_loop, vars_matrix, rtol=1e-8), "两种方法结果不一致！"

print(f"\n  🐌 for 循环:       {time_loop * 1000:.1f} ms")
print(f"  🚀 矩阵批量运算:   {time_matrix * 1000:.2f} ms")
print(f"  加速比: {time_loop / time_matrix:.0f}x")
print("\n  💡 批量矩阵运算利用了 BLAS 的并行能力，M 越大优势越明显。")


# ==========================================
# 📊 5. 风险-收益散点图（有效前沿 Monte Carlo 版）
# ==========================================
print("\n" + "=" * 60)
print("📊 风险-收益云图（M 个随机组合的展布）")
print("=" * 60)

# 年化收益期望：μ_annualized = (1 + μ_daily)^252 - 1
# 用算术均值代替几何均值（小值近似：μ_ann ≈ μ * 252）
mu_daily = mu                                     # (N,)
mu_ann   = mu_daily * 252                         # 简化年化（用于显示）
sigma_ann = np.sqrt(np.diag(Sigma)) * np.sqrt(252)  # (N,) 各股年化波动率

# 计算每个随机组合的年化收益 & 年化波动
port_ret_ann  = W_all @ mu_ann         # (M,)  组合年化收益
port_var      = vars_matrix            # (M,)  组合日度方差
port_sigma_ann = np.sqrt(port_var) * np.sqrt(252)  # (M,) 组合年化波动率

# 年化夏普（无风险率=0，简化）
port_sharpe = port_ret_ann / port_sigma_ann

print(f"\n  收益率范围: [{port_ret_ann.min()*100:.2f}%, {port_ret_ann.max()*100:.2f}%]")
print(f"  波动率范围: [{port_sigma_ann.min()*100:.2f}%, {port_sigma_ann.max()*100:.2f}%]")
print(f"  夏普比范围: [{port_sharpe.min():.3f}, {port_sharpe.max():.3f}]")

# 找最小方差组合（MVP）
idx_min_var = np.argmin(port_var)
w_mvp       = W_all[idx_min_var]

# 找最高夏普组合
idx_max_sharpe = np.argmax(port_sharpe)
w_max_sharpe   = W_all[idx_max_sharpe]


# ==========================================
# 🏆 6. 三种典型组合对比
# ==========================================
print("\n" + "=" * 60)
print("🏆 三种典型组合对比")
print("=" * 60)

def portfolio_stats(w, label):
    """计算并打印组合的关键指标"""
    var_p  = w @ Sigma @ w
    ret_p  = w @ mu_ann
    sig_p  = np.sqrt(var_p) * np.sqrt(252)
    sharpe = ret_p / sig_p if sig_p > 0 else 0
    print(f"\n  {'─'*54}")
    print(f"  📌 {label}")
    print(f"     权重: {dict(zip(selected, w.round(4)))}")
    print(f"     年化收益 : {ret_p*100:>8.3f}%")
    print(f"     年化波动 : {sig_p*100:>8.3f}%")
    print(f"     夏普比例 : {sharpe:>8.3f}")
    return ret_p, sig_p, sharpe

r1, s1, sh1 = portfolio_stats(w_equal,       "等权组合 (1/N)")
r2, s2, sh2 = portfolio_stats(w_mvp,         "最小方差组合 (MVP)")
r3, s3, sh3 = portfolio_stats(w_max_sharpe,  "最高夏普组合")

print(f"\n{'─'*54}")
print(f"\n  🗺️  各单股 年化风险-收益 概览:")
print(f"  {'标的':<12} {'年化收益%':>10} {'年化波动%':>10} {'夏普比':>8}")
print(f"  {'─'*42}")
for i, sym in enumerate(selected):
    w_single = np.zeros(N); w_single[i] = 1.0
    r_s = w_single @ mu_ann
    s_s = np.sqrt(w_single @ Sigma @ w_single) * np.sqrt(252)
    sh_s = r_s / s_s if s_s > 0 else 0
    print(f"  {sym:<12} {r_s*100:>10.3f} {s_s*100:>10.3f} {sh_s:>8.3f}")


# ==========================================
# 🧠 7. 维度映射 Cheat Sheet
# ==========================================
print("\n" + "=" * 60)
print("🧠 Week 3 维度总地图 (Day 1 → Day 4)")
print("=" * 60)
print(f"""
  对象               含义                    shape
  ──────────────────────────────────────────────────
  w  (权重)          投资者可控旋钮           ({N},)
  μ  (均值)          各股平均日收益           ({N},)
  R  (收益矩阵)      历史日度收益率           ({T}, {N})
  Σ  (协方差矩阵)    资产风险-相关结构        ({N}, {N})

  运算链                代码                  结果 shape
  ──────────────────────────────────────────────────
  Day1  单日组合收益   w @ r_t               标量 ()
  Day1  全量组合收益   R @ w                 ({T},)
  Day3  协方差矩阵     R_c.T @ R_c / (T-1)  ({N}, {N})
  Day4  组合方差       w.T @ Σ @ w           标量 ()
  Day4  一次批量评估   (W@Σ)*W .sum()        ({M:,},)
  
  马科维茨核心公式:
    σ²_p = w^T · Σ · w
    
  这是一个二次型 (quadratic form):
  w 是线性变量，Σ 是"曲率矩阵"，输出是标量风险度量。
  后续优化 (min σ²_p s.t. Σw=1, w·μ≥r_target) 就是在这之上加约束。
""")


# ==========================================
# ✅ 8. 自测断言汇总
# ==========================================
print("✅ 运行自测断言...")

# 1. Σ 是正定的（所有特征值 > 0）
eigenvalues = np.linalg.eigvalsh(Sigma)
assert np.all(eigenvalues > 0), f"Σ 不是正定矩阵! 最小特征值={eigenvalues.min()}"
print("  1. Σ 是正定矩阵 ✅")

# 2. Σ 是对称矩阵
assert np.allclose(Sigma, Sigma.T), "Σ 不是对称矩阵！"
print("  2. Σ 是对称矩阵 ✅")

# 3. 对任意合法权重 w，组合方差 > 0
for _ in range(100):
    w_rnd = np.random.dirichlet(np.ones(N))
    assert w_rnd @ Sigma @ w_rnd > 0
print("  3. 随机 100 组权重，组合方差均 > 0 ✅")

# 4. MVP 方差 <= 等权方差
assert w_mvp @ Sigma @ w_mvp <= w_equal @ Sigma @ w_equal + 1e-10, "MVP 方差应最小！"
print("  4. MVP 方差 <= 等权组合方差 ✅")

# 5. 单资产退化验证: w=[0,..,1,..,0] → σ_p == σ_i
for i in range(N):
    w_single = np.zeros(N); w_single[i] = 1.0
    var_single = w_single @ Sigma @ w_single
    assert np.isclose(var_single, Sigma[i, i]), f"单资产方差与对角线不符! idx={i}"
print("  5. 单资产权重退化 → Σ[i,i] ✅")

print("\n  全部通过 ✅")

print(f"\n{'='*60}")
print("📌 Day 4 总结")
print(f"{'='*60}")
print(f"""
  ✅ 掌握：σ²_p = w^T @ Σ @ w 的逐步推导（二次型）
  ✅ 验证：解析公式 == 历史序列 .std()，两种视角统一
  ✅ 实战：Monte Carlo 随机权重扫描，刻画风险-收益云图
  ✅ 发现：等权 / 最小方差 / 最高夏普 三种典型组合的差异
  ✅ 性能：批量矩阵化 (W@Σ)*W 比 for 循环快 {int(time_loop/time_matrix)}x

  Week 3 核心线索回顾:
    Day 1  w · r        → 向量点乘，单日组合收益
    Day 2  * vs @       → 逐元素 vs 矩阵乘法，BLAS 威力
    Day 3  R^T @ R / T  → 手撸协方差矩阵 Σ
    Day 4  w^T @ Σ @ w  → 组合方差，马科维茨风险度量 ← 今天

  🔜 Week 4: 真正的马科维茨优化
     min  w^T @ Σ @ w
     s.t. w^T @ μ >= r_target
          Σ_i w_i = 1
          w_i >= 0
     用 scipy.optimize 或解析解求出有效前沿！
""")
