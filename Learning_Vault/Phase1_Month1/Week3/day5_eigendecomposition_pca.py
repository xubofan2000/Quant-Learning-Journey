"""
day5_eigendecomposition_pca.py - Week 3 Day 5: 特征值分解与PCA市场因子初探

核心认知跃迁：
    Day 3 手撸出了 N×N 的协方差矩阵 Σ，它浓缩了所有资产间的波动联动，
    但一团密集的数字很难直接"看懂"市场里有哪几股主要风险力量。

    今天用线性代数的解剖刀——特征值分解（Eigendecomposition）来拆解 Σ：
        Σ = Q @ Λ @ Q.T
    - Λ 对角线上是特征值 λ₁ ≥ λ₂ ≥ ... ≥ λₙ，代表对应"方向"的方差贡献量
    - Q 的每一列是一个"主方向"（主成分），最大特征值对应的方向 ≈ 市场 Beta 因子

目标：
1. 用 scipy.linalg.eigh 对协方差矩阵做特征值分解
2. 理解每个特征值的"方差解释率"，定位支配市场的主要风险方向
3. 验证第一主成分 ≈ 市场 Beta 因子，并用重构校验数学完备性
"""

# %% [0. 导入依赖库]
# numpy  : 数值计算核心，提供 ndarray、矩阵运算、线性代数基础
# pandas : 表格数据处理，负责读取 parquet 和 pivot_table 等操作
# scipy.linalg : SciPy 的线性代数模块，提供比 numpy.linalg 更完整的矩阵分解工具
#   → 今天用 sla.eigh，专门针对实对称矩阵做特征值分解
# os : 标准库，用于路径拼接，实现跨平台的文件定位
import numpy as np
import pandas as pd
import scipy.linalg as sla
import os

print("✅ 依赖库导入完成")

# %% [1. 数据加载]
# 【编程概念】__file__ 是 Python 的内置变量，存储当前脚本的路径字符串。
#   os.path.abspath() 将相对路径转为绝对路径。
#   组合使用可以实现"相对于脚本文件本身定位"，无论在哪个目录执行都能找到正确路径。
#   这是量化工程中的基础规范：禁止硬编码 'D:\\project\\...' 这样的绝对路径。
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
parquet_path = os.path.join(project_root, 'Database', 'files', 'panel_50stocks.parquet')

# 【数据格式】Parquet 是列式存储格式，读取速度远超 CSV（只加载需要的列，不扫全表）
df_panel = pd.read_parquet(parquet_path)

selected = ['SIM0001', 'SIM0010', 'SIM0020', 'SIM0035', 'SIM0050']
print(f"面板数据维度: {df_panel.shape}")   # (总行数, 列数)，每行是一只股票某天的记录
print(f"选取标的: {selected}")
print(f"\n数据预览（长表格式）:")
print(df_panel[df_panel['symbol'].isin(selected)].head(3))

# %% [2. 长表 → 宽表：pivot_table]
# 【金融概念】面板数据（Panel Data）有两种存储形态：
#   - 长表（Long format）：每行 = (股票, 日期, 收益率)，行数 = N只 × T天
#   - 宽表（Wide format）：每行 = 某天的所有股票收益，列数 = N只，行数 = T天
#
# 【编程概念】pivot_table 是"行列互换 + 聚合"的操作：
#   index='trade_date'  → 日期变成行索引
#   columns='symbol'    → 股票代码变成列名
#   values='daily_return' → 填入该格子对应的收益率值
#   .dropna()           → 删除含 NaN 的行（保证矩阵完整性）
df_returns = df_panel[df_panel['symbol'].isin(selected)].pivot_table(
    index='trade_date',
    columns='symbol',
    values='daily_return'
).dropna()

print(f"宽表 df_returns.shape = {df_returns.shape}")  # (T天, N只)
print("\n宽表末尾 3 行（每列是一只股票的日收益率）:")
print(df_returns.tail(3))

# %% [3. 转为 NumPy 矩阵 R，并去均值]
# 【数学概念】去均值（Mean Centering / Demeaning）：
#   R_centered = R - μ
#   目的：让矩阵只保留"波动"信息，消除均值漂移的干扰。
#   协方差矩阵描述的是"偏离均值的联动"，所以必须先去均值。
#
# 【编程概念】Broadcasting（广播）：
#   R 的 shape 是 (T, N)，mu 的 shape 是 (N,)
#   Python 会自动把 mu 扩展成 (1, N) → (T, N) 再做减法，无需手动循环
R = df_returns.values       # DataFrame → NumPy 数组，shape: (T, N)
T, N = R.shape
mu = R.mean(axis=0)         # axis=0 表示沿行方向求均值，得到每列（每只股票）的均值
R_centered = R - mu         # Broadcasting: 每一行都减去对应列的均值

print(f"R.shape = {R.shape}   # (T={T}天, N={N}只)")
print(f"mu 各股日均收益: {mu.round(6)}")
# 验证：去均值后的均值应该 ≈ 0（浮点数精度误差）
print(f"R_centered 列均值（应≈0）: {R_centered.mean(axis=0).round(12)}")

# %% [4. 复现 Day3 协方差矩阵 Σ]
# 【数学公式】协方差矩阵：
#   Σ = (R_c.T @ R_c) / (T - 1)
#   其中 R_c 是去均值后的收益矩阵（shape: T×N）
#
#   矩阵乘法维度推导：
#   R_c.T  shape: (N, T)
#   R_c    shape: (T, N)
#   乘积   shape: (N, N)  ← 这就是 N×N 的协方差矩阵
#
# 【统计概念】除以 (T-1) 而非 T：这叫"无偏估计（Bessel's correction）"
#   样本方差用 T-1 修正，避免对总体方差的系统性低估（自由度损失 1）
Sigma = (R_centered.T @ R_centered) / (T - 1)

print(f"Sigma.shape = {Sigma.shape}   # N×N 对称矩阵")
print("Sigma 的值（放大 10⁴ 倍方便阅读）:")
print(np.round(Sigma * 1e4, 3))
# 验证：对角线元素 = 各股的方差（协方差矩阵的定义）
print(f"\n对角线（各股方差）: {np.diag(Sigma).round(6)}")
assert np.allclose(np.diag(Sigma), np.var(R, axis=0, ddof=1))
print("✅ 对角线 == np.var(R, ddof=1)，协方差矩阵构造正确")

# %% [5. 特征值分解：为什么用 eigh 而不是 eig？]
# 【数学概念】特征值分解（Eigendecomposition）：
#   对于方阵 A，如果存在非零向量 v（特征向量）和标量 λ（特征值）使得：
#       A @ v = λ * v
#   那么 A 可以分解为：A = Q @ Λ @ Q⁻¹
#   对于实对称矩阵（如协方差矩阵 Σ），Q 是正交矩阵（Q⁻¹ = Q.T），所以：
#       Σ = Q @ Λ @ Q.T
#
# 【编程概念】scipy.linalg.eigh vs scipy.linalg.eig：
#   eig  → 通用特征值分解，输出可能含复数，特征值无序，速度较慢
#   eigh → 专门针对实对称（Hermitian）矩阵，保证：
#           · 特征值全为实数（协方差矩阵一定满足正半定，特征值 ≥ 0）
#           · 特征值升序排列（从小到大）
#           · 比 eig 更快、数值更稳定
eigenvalues_raw, eigenvectors_raw = sla.eigh(Sigma)

print("eigh 原始输出（升序）:")
print(f"  eigenvalues = {eigenvalues_raw.round(6)}")
print(f"  eigenvectors.shape = {eigenvectors_raw.shape}   # 每列是一个特征向量")
print(f"  特征值全为实数: {np.isreal(eigenvalues_raw).all()}")
print(f"  特征值全 ≥ 0（正半定）: {(eigenvalues_raw >= -1e-10).all()}")

# %% [6. 翻转为降序（最重要的因子排第一）]
# 【编程技巧】NumPy 的反转切片：
#   一维数组翻转：arr[::-1]         → 步长 -1，从末尾往前取
#   二维数组按列翻转：arr[:, ::-1]  → 列方向步长 -1，行方向不变
#   注意：特征向量按列存储，所以必须用 [:, ::-1]，不能用 [::-1]（那会翻转行）
eigenvalues = eigenvalues_raw[::-1]
eigenvectors = eigenvectors_raw[:, ::-1]

print("特征值降序排列，及其对应的年化波动率等效:")
print("  （λ 是日度方差，× 252 个交易日 = 年化方差，再开根号 = 年化波动率）")
for i, lam in enumerate(eigenvalues):
    ann_vol = np.sqrt(lam * 252) * 100
    print(f"  λ{i+1} = {lam:.6f}  →  年化波动率等效: {ann_vol:.2f}%")

# %% [7. 方差解释率（Explained Variance Ratio）]
# 【统计概念】方差解释率：
#   每个主成分（特征向量方向）解释了总方差的多少比例
#   公式：ratio_i = λ_i / Σ(所有λ)
#   累计解释率：cumsum(ratio)，表示前 k 个主成分共同解释的方差比例
#
# 【金融直觉】在真实 A 股数据中：
#   PC1（第一主成分）通常解释 60-70% 的总方差 → 市场整体涨跌（系统性风险）
#   PC2-3 解释行业轮动等次级风险
#   这也是 Barra 多因子模型的数学基础
total_variance = eigenvalues.sum()
explained_ratio = eigenvalues / total_variance
cumulative_ratio = np.cumsum(explained_ratio)

print("主成分  |  特征值     |  解释率   |  累计解释率  |  柱状图")
print("-" * 65)
for i in range(N):
    bar = "█" * int(explained_ratio[i] * 30)
    print(f"  PC{i+1}   |  {eigenvalues[i]:.6f}  |  {explained_ratio[i]*100:5.1f}%   |"
          f"   {cumulative_ratio[i]*100:5.1f}%    |  {bar}")
print(f"\n💡 PC1 独自解释了 {explained_ratio[0]*100:.1f}% 的总方差")
print("   （模拟数据相关性较弱，真实A股通常 PC1 > 60%）")

# %% [8. 第一特征向量 q₁：各股票的因子载荷（Factor Loading）]
# 【金融概念】因子载荷（Loading）：
#   q₁ 是 Σ 中"方差贡献最大的方向"，是一个 N 维向量
#   q₁[i] 表示第 i 只股票在这个"主方向"上的暴露程度（权重）
#
#   如果所有资产的载荷符号相同（全正或全负）→ q₁ 代表"所有资产同涨同跌"
#   这就是市场整体 Beta 因子（系统性风险）的数学表达
#
# 【数学说明】特征向量的方向有符号任意性：
#   如果 v 是特征向量，-v 同样是特征向量（方向相反但等价）
#   所以"全负"和"全正"在金融含义上是相同的（同向暴露）
q1 = eigenvectors[:, 0]     # 取第一列 = 第一主成分的方向向量，shape: (N,)

print("q₁ 各资产因子载荷（Loading）:")
for sym, loading in zip(selected, q1):
    direction = "↑" if loading > 0 else "↓"
    bar = "█" * int(abs(loading) * 40)
    print(f"  {sym}: {loading:+.4f}  {direction}  {bar}")

all_same_sign = np.all(q1 > 0) or np.all(q1 < 0)
print(f"\n载荷全部同向: {all_same_sign}")
print("→ 若全同向，q₁ 就是'所有资产同涨同跌'的市场系统性风险因子（Beta）")

# %% [9. 主成分得分序列：将原始数据投影到特征向量空间]
# 【数学概念】PCA 的降维操作（投影 / Projection）：
#   scores = R_centered @ eigenvectors
#   维度推导：(T, N) @ (N, N) → (T, N)
#   含义：把每个交易日的 N 维收益向量，转换为 N 个主成分坐标
#   scores[:, 0] = PC1 的时间序列得分，表示"市场整体因子"每天的强弱
#
# 【金融验证】如果 PC1 ≈ 市场 Beta 因子：
#   PC1 得分时间序列应与"等权组合收益"高度相关（因为等权组合是最朴素的市场代理）
#   Pearson 相关系数 |r| > 0.9 → 强相关，可认定 PC1 捕捉了市场整体走势
scores = R_centered @ eigenvectors          # (T, N) @ (N, N) → (T, N)
pc1_series = scores[:, 0]                   # PC1 时间序列，shape: (T,)
equal_weight = R_centered @ np.ones(N) / N  # 等权组合收益序列，shape: (T,)

corr = np.corrcoef(pc1_series, equal_weight)[0, 1]
print(f"PC1 得分序列 shape: {pc1_series.shape}   # T 个交易日的因子强度")
print(f"PC1 vs 等权组合 Pearson 相关系数: {corr:.4f}")
print(f"{'✅ |r|>0.9，PC1 确实捕捉了市场整体走势（Beta因子）' if abs(corr) > 0.9 else '📌 相关性适中，可能是模拟数据的低相关性特性'}")

# %% [10. 数学完备性验证：从特征值重构 Σ]
# 【数学验证】特征值分解的核心等式：
#   Σ = Q @ diag(λ) @ Q.T
#   其中 diag(λ) 是以特征值为对角线元素的对角矩阵
#
#   如果分解正确，重构出的矩阵应与原始 Σ 完全一致。
#   误差量级应接近机器精度（float64 ≈ 1e-16），远小于 1e-10。
#
# 【编程概念】np.diag(v)：
#   当 v 是一维数组时 → 生成以 v 为对角线的方阵
#   当 v 是二维矩阵时 → 提取对角线元素（功能相反，注意区分）
Sigma_reconstructed = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T

max_error = np.abs(Sigma - Sigma_reconstructed).max()
print(f"重构最大绝对误差: {max_error:.2e}")
print(f"（float64 机器精度约为 {np.finfo(float).eps:.2e}，误差应在此量级）")
assert max_error < 1e-10, "重构误差过大，请检查分解过程！"
print("✅ Σ = Q @ Λ @ Q.T 完美成立")
print("\n🎯 Day 5 全部完成！特征值分解 → 方差解释率 → Beta因子识别 → 重构验证")

# %%