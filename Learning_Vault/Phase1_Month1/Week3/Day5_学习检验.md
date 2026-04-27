# 📚 Week 3 Day 5 学习检验（最终版）
# 特征值分解与PCA市场因子初探
# 对应代码：day5_eigendecomposition_pca.py

---

## 🃏 闪卡（概念验证）

---

**Q1【编程】**：`scipy.linalg.eigh` 和 `scipy.linalg.eig` 都能做特征值分解，对协方差矩阵你该选哪个？给出至少 3 条理由。

<details><summary>答案</summary>

选 **`eigh`**，专门针对实对称/埃尔米特矩阵：

| 对比点 | `eig`（通用） | `eigh`（对称专用） |
|--------|-------------|-----------------|
| 特征值类型 | 可能含复数 | **保证全为实数** |
| 特征值顺序 | 无序 | **升序排列** |
| 速度 | 慢 | **更快、数值更稳定** |
| 适用条件 | 任意方阵 | 实对称/埃尔米特矩阵 |

协方差矩阵 Σ 一定是实对称矩阵（$\Sigma = \Sigma^T$），且正半定（所有特征值 ≥ 0），选 `eigh` 是正确且高效的选择。

</details>

---

**Q2【数学】**：`eigh` 返回的特征值是**升序**的。用 NumPy 切片将一维特征值数组和二维特征向量矩阵同时翻转为降序，分别怎么写？两者有什么不同？

<details><summary>答案</summary>

```python
eigenvalues  = eigenvalues_raw[::-1]       # 一维：步长 -1，从末尾往前取
eigenvectors = eigenvectors_raw[:, ::-1]   # 二维：列方向翻转，行方向不变
```

**关键区别**：特征向量按**列**存储（每列是一个特征向量），所以必须用 `[:, ::-1]` 翻转列，不能用 `[::-1]`——那样会翻转**行**，把每个特征向量内部的元素顺序打乱，完全错误。

</details>

---

**Q3【数学+金融】**：什么是"方差解释率（Explained Variance Ratio）"？写出公式，并解释 PC1 在金融上代表什么。

<details><summary>答案</summary>

**公式**：

$$\text{ratio}_i = \frac{\lambda_i}{\sum_{j=1}^{N} \lambda_j}$$

每个特征值除以所有特征值的总和，表示这个主成分方向解释了多少比例的总风险。

**金融含义**：  
- PC1（最大特征值对应的方向）通常解释最多的方差，在真实 A 股中约占 60-70%。  
- PC1 对应的特征向量 q₁ 的各资产载荷（Loading）若全部同向 → 这个方向代表"所有资产同涨同跌"的**市场 Beta 因子**（系统性风险）。  
- 这是 Barra 多因子模型"市场因子"的数学起源。

</details>

---

**Q4【数学】**：特征值分解的核心等式是什么？如何用代码验证"分解后能完整还原原矩阵"？误差量级应在什么范围内？

<details><summary>答案</summary>

核心等式：$\Sigma = Q \cdot \Lambda \cdot Q^T$

```python
Sigma_reconstructed = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T
max_error = np.abs(Sigma - Sigma_reconstructed).max()
assert max_error < 1e-10
```

误差应接近 **float64 机器精度**（约 `2.22e-16`），今天实测为 `2.71e-19`，完全在数值精度范围内。

**注意**：`np.diag(v)` 当 `v` 是一维数组时，生成以 `v` 为对角线的方阵；当 `v` 是二维矩阵时，则是提取对角线元素——两个方向功能相反，注意区分。

</details>

---

**Q5【金融】**：什么是"因子载荷（Factor Loading）"？如果 q₁ 的载荷出现异号（有正有负），意味着什么？如果全部同号，意味着什么？

<details><summary>答案</summary>

**因子载荷**：特征向量 q₁ 中第 i 个元素 q₁[i]，表示第 i 只资产在这个主成分方向上的暴露程度（类似权重）。

- **全部同号（全正或全负）** → q₁ 代表所有资产同向运动的方向，即**市场整体 Beta 因子**（系统性风险）。注：特征向量有"符号任意性"，全负和全正在金融含义上等价。
- **出现异号** → q₁ 捕捉的是某种"相对运动"，例如某只股票与其他股票的分化走势（可能是某资产特有风险或行业对冲关系），不是市场因子。

今天的模拟数据中 SIM0050 载荷 = -0.997，其余接近 0，说明 PC1 几乎被 SIM0050 主导，这是模拟数据相关性低的结果。

</details>

---

## 💻 代码习题

---

### 题目 1【形状推演 × 填空】

给定以下已知变量，完成特征值分解和数据投影，并在每处填写正确代码和预期的输出 shape：

```python
import numpy as np
import scipy.linalg as sla

# 已知：R_centered.shape = (1735, 5)，Sigma.shape = (5, 5)

# Step 1: 分解 Sigma
eigenvalues_raw, eigenvectors_raw = ___________   # eigenvalues_raw.shape = ?

# Step 2: 翻转为降序
eigenvalues  = ___________   # shape: (5,)
eigenvectors = ___________   # shape: (5, 5)

# Step 3: 计算方差解释率
explained_ratio = ___________   # shape: ?

# Step 4: 将 R_centered 投影到特征向量空间
scores = ___________   # shape = ?，推演过程：(?, ?) @ (?, ?) → (?, ?)

# Step 5: 提取 PC1 时间序列
pc1 = ___________   # shape = ?
```

> 重点：在填写 Step 4 之前，先用注释写出矩阵乘法的维度推演过程。

<details><summary>参考答案</summary>

```python
eigenvalues_raw, eigenvectors_raw = sla.eigh(Sigma)
# eigenvalues_raw.shape = (5,)  ← 一维向量，N 个特征值

eigenvalues  = eigenvalues_raw[::-1]
eigenvectors = eigenvectors_raw[:, ::-1]

explained_ratio = eigenvalues / eigenvalues.sum()
# shape: (5,)  ← 每个特征值对应一个解释率

# 维度推演：R_centered (1735, 5) @ eigenvectors (5, 5) → (1735, 5)
scores = R_centered @ eigenvectors

pc1 = scores[:, 0]   # shape: (1735,)  ← 取第一列
```

</details>

---

### 题目 2【改错】

下面的代码试图验证"PC1 近似等于市场 Beta 因子"，但有 **2 处错误**，找出并修正：

```python
# 已有：scores.shape = (1735, 5)，equal_weight.shape = (1735,)

# ❌ 错误写法
pc1_series = scores[0, :]                    # 取第一行
corr_matrix = np.corrcoef(scores, equal_weight)
corr = corr_matrix[0, 1]
print(f"PC1 与等权组合相关系数: {corr:.4f}")
```

<details><summary>答案</summary>

**错误 1**：`scores[0, :]` 取的是第一**行**（第一个交易日的所有 PC 得分），应该取第一**列**（PC1 的时间序列）：
```python
pc1_series = scores[:, 0]   # ✅ shape: (1735,)
```

**错误 2**：`np.corrcoef(scores, equal_weight)` 把二维的 `scores`（1735×5）和一维的 `equal_weight` 传进去，会报维度错误或得到错误结果。应该只传 PC1 序列：
```python
corr_matrix = np.corrcoef(pc1_series, equal_weight)   # ✅ 两个 (1735,) 向量
corr = corr_matrix[0, 1]
```

</details>

---

### 题目 3【金融直觉】

以下是今天的实验结果：

```
PC1 解释率: 37.7%
q₁ 载荷: SIM0001=-0.047, SIM0010=+0.006, SIM0020=+0.055, SIM0035=+0.017, SIM0050=-0.997
PC1 vs 等权组合相关系数: -0.60
```

请回答：
1. 为什么 PC1 的解释率只有 37.7%，而不是真实 A 股常见的 60%+？
2. 为什么 PC1 与等权组合的相关系数只有 -0.60 而不是更高？
3. q₁ 载荷中 SIM0050 接近 -1、其余接近 0 说明了什么？

<details><summary>答案</summary>

1. **解释率低（37.7%）**：因为数据是**模拟生成**（SIM 前缀），相关性是人工合成的，5 只股票之间协方差很小（Σ 的非对角线元素量级 ~10⁻⁵，远小于对角线）。真实 A 股受同一宏观环境驱动，整体联动性强，PC1 自然解释更多。

2. **相关系数只有 -0.60**：PC1 被 SIM0050 主导（见下），而等权组合是5只股票均等混合。SIM0050 波动最大（年化 49.7%），其他股票权重被"稀释"，导致 PC1 与等权组合的相关性不高（绝对值 0.60，不是 >0.9 的强相关）。

3. **SIM0050 ≈ -1，其余 ≈ 0**：PC1 几乎完全由 SIM0050 的方差贡献（它的日方差 ~9.77×10⁻⁴，是其他股票的 2-4 倍）。这个方向不是"市场整体 Beta"，而是"SIM0050 独自的大波动方向"。这正是模拟数据与真实数据的核心差异。

</details>
