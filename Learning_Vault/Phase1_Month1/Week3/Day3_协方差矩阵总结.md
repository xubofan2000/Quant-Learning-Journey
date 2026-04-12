# Day 3 - 手撸协方差矩阵 (Covariance Matrix)

> Week 3 主题：从理论到代码 — 线性代数与资产组合映射
> 今天是第三天：从零推导 Markowitz 风控的"心脏"——协方差矩阵 Σ，并 assert 验证手工结果与 `np.cov()` 完全一致。

## 🎯 核心认知

**协方差矩阵 Σ 是马科维茨风险评估的心脏**

```
对角线 Σ[i,i] = 股票 i 的方差（自身波动性）
非对角线 Σ[i,j] = 股票 i 与 j 的协方差（联动方向与强度）
```

- 正协方差 → 两只股票涨跌方向一致（共振放大风险）
- 负协方差 → 跌的时候另一个涨（天然对冲，是分散化的来源）
- 到了 Day 4，用它算组合方差：`σ_p² = w^T @ Σ @ w`

## 🧮 四步推导公式

```
1. 均值向量:   μ = R.mean(axis=0)                     shape: (N,)
2. 去中心化:   R_centered = R - μ                      shape: (T, N)  [Broadcasting]
3. 叉乘求和:   S = R_centered.T @ R_centered            shape: (N, N)  [内维 T 坍缩]
4. 无偏修正:   Σ = S / (T - 1)                         shape: (N, N)
```

**除以 T-1 而不是 T**：这是样本无偏估计（Bessel's correction），避免低估总体方差。

## 💻 核心代码（完整推导）

```python
# Step 1 & 2: 均值 + 去中心化
mu = R.mean(axis=0)           # (N,)
R_centered = R - mu           # Broadcasting: (T,N) - (N,) → (T,N)

# Step 3 & 4: 矩阵叉乘 + 自由度修正
cov_manual = (R_centered.T @ R_centered) / (T - 1)

# 验证与 np.cov 完全一致
cov_numpy = np.cov(R, rowvar=False)
assert np.allclose(cov_manual, cov_numpy)   # ✅ 完美一致

# 顺便验证对角线 = 各自的样本方差
assert np.allclose(np.diag(cov_numpy), np.var(R, axis=0, ddof=1))
```

**注意 `rowvar=False`**：`np.cov` 默认每行是一个变量（`rowvar=True`）；我们的矩阵是 (T×N)，每**列**是一只股票，必须指定 `rowvar=False`，或者传 `R.T`。

## 📐 维度 Cheat Sheet

| 对象 | 含义 | shape |
|------|------|-------|
| `R` | 收益率原矩阵（历史数据） | `(T, N)` |
| `μ` | 各股日均收益 | `(N,)` |
| `R_centered` | 去均值后的超额收益 | `(T, N)` |
| `R_centered.T` | 转置 | `(N, T)` |
| `R_centered.T @ R_centered` | 平方和矩阵 | `(N, N)` ← T 坍缩 |
| **`Σ`（协方差矩阵）** | 风险结构图 | `(N, N)` |

**推导路径记忆**：
```
(N, T)  @  (T, N)  →  (N, N)
         ↑ 内维 T 相乘并坍缩
```

## ⏱️ 性能实测（50只股票，500次循环）

| 方法 | 特点 | 相对速度 |
|------|------|---------|
| 🐌 `df.cov()` | Pandas，含索引对齐和 NaN 检查 | 1x（基准） |
| 🚶 `np.cov(rowvar=False)` | NumPy，较干净 | 数倍于 Pandas |
| 🚀 **纯 NumPy：`R^T @ R`** | **BLAS 矩阵乘法** | **最快（数倍~十倍于 np.cov）** |

**根因**：`R_centered.T @ R_centered` 直接调用 BLAS 的 `dgemm`（通用矩阵乘法），没有任何 Python 层对象开销。`np.cov` 额外有一些 Python 检查；Pandas 再加了索引对齐层。

## ⚠️ 典型陷阱

1. **忘了去中心化** → `R.T @ R / (T-1)` 算出来的是**原点矩（second moment）**，不是协方差矩阵
2. **除以 T 而非 T-1** → 有偏估计，在小样本下会系统性低估方差
3. **`np.cov` 忘了 `rowvar=False`** → 算出来是 `(T, T)` 大矩阵，每天作为一个"变量"，完全错误
4. **混用对数/简单收益率** → Day 1 的铁律：组合横截面加权用**简单收益率**

## 🔍 关键洞察

1. **协方差矩阵是对称的** — `Σ[i,j] == Σ[j,i]`，所以只有 N(N+1)/2 个独立数字
2. **对角线就是方差** — `np.diag(Σ) == np.var(R, ddof=1)`，协方差矩阵统一了方差和协方差
3. **去中心化的本质** — 消除均值漂移，让矩阵叉乘计算的是"波动的相关性"而不是绝对收益的相关性
4. **Σ 是正半定矩阵** — 它的特征值全部 ≥ 0，这保证了 `w^T @ Σ @ w ≥ 0`（组合方差不为负）

## 🧠 金融直觉

协方差矩阵是一张**资产间风险纠缠的地图**：

```
Σ = | Var(SIM0001)          Cov(SIM0001, SIM0025)  Cov(SIM0001, SIM0050) |
    | Cov(SIM0025, SIM0001) Var(SIM0025)            Cov(SIM0025, SIM0050) |
    | Cov(SIM0050, SIM0001) Cov(SIM0050, SIM0025)  Var(SIM0050)           |
```

- 如果两只股票 Cov > 0，放在一起**不会**降低风险（同涨同跌）
- 如果 Cov < 0，两者天然对冲，组合方差 < 各自方差的加权和
- **Markowitz 的本质**：通过调整 w，在不改变行情的前提下，选择风险最小（或夏普最大）的权重

## 💡 与前两天的衔接

| Day | 核心操作 | shape |
|-----|---------|-------|
| Day 1 | `R @ w` | (T,N) @ (N,) → (T,) 每天组合收益 |
| Day 2 | `R * w` vs `R @ w` | 展开 vs 压缩的本质区别 |
| **Day 3** | **`R_c.T @ R_c / (T-1)`** | **(T,N)^T @ (T,N) → (N,N) 风险地图** |
| Day 4 预告 | `w.T @ Σ @ w` | 标量，组合总方差 |

## 🔜 明天预告

**Day 4: 马科维茨组合方差**
- 利用今天的 Σ，计算 `σ_p² = w^T @ Σ @ w`
- 验证：调整权重 w 如何影响组合总风险
- 为均值-方差优化（有效前沿）打下最后一块基石
