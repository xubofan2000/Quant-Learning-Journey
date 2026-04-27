# Week 3 Day 5: 特征值分解与PCA市场因子初探 (Eigendecomposition · scipy.linalg.eigh)

---

## 1. 核心认知：协方差矩阵的"解剖"

Day 3 我们构造了协方差矩阵 Σ，今天用**特征值分解**把它拆开来看：

$$\Sigma = Q \cdot \Lambda \cdot Q^T$$

| 符号 | 含义 | Shape |
|------|------|-------|
| $\Sigma$ | 协方差矩阵（对称正半定） | (N, N) |
| $Q$ | 特征向量矩阵，每**列**是一个主方向 | (N, N) |
| $\Lambda$ | 对角矩阵，对角线是特征值 $\lambda_1 \geq \lambda_2 \geq \ldots$ | (N, N) |

**直觉**：Σ 浓缩了 N 只资产的联动关系，但难以直读。特征值分解相当于把 N 维风险空间"旋转"到最自然的坐标轴上，每根轴（主成分）互相正交，第一根轴指向"方差最大的方向"。

### 关键代码

```python
# eigh 专用于实对称矩阵：保证实数特征值 + 升序排列 + 比 eig 更快
eigenvalues_raw, eigenvectors_raw = sla.eigh(Sigma)

# eigh 升序 → 翻转为降序（最重要的因子排第一）
# 一维数组翻转：[::-1]；特征向量按列存，列方向翻转：[:, ::-1]
eigenvalues  = eigenvalues_raw[::-1]
eigenvectors = eigenvectors_raw[:, ::-1]
```

> ⚠️ 容易犯的错：`eigenvectors[::-1]` 是翻转**行**（打乱每个特征向量的内部顺序），必须用 `[:, ::-1]` 翻转**列**。

---

## 2. 方差解释率与市场 Beta 因子

### 2.1 方差解释率

$$\text{ratio}_i = \frac{\lambda_i}{\sum_{j=1}^{N} \lambda_j}$$

```python
explained_ratio  = eigenvalues / eigenvalues.sum()   # shape: (N,)
cumulative_ratio = np.cumsum(explained_ratio)
```

今天实验结果（模拟数据 5 只股票）：

| 主成分 | 特征值 | 解释率 | 累计 |
|--------|--------|--------|------|
| PC1 | 0.000980 | **37.7%** | 37.7% |
| PC2 | 0.000593 | 22.8% | 60.5% |
| PC3-5 | ... | 39.5% | 100% |

真实 A 股中 PC1 通常 >60%，模拟数据偏低是因为股票间相关性人工合成、联动性弱。

### 2.2 第一主成分 ≈ 市场 Beta 因子

```python
q1 = eigenvectors[:, 0]      # 第一主成分方向，shape: (N,)

# 验证：将 R_centered 投影到特征向量空间
# 维度推演：(T, N) @ (N, N) → (T, N)，每列是一个主成分的时间序列
scores = R_centered @ eigenvectors
pc1_series = scores[:, 0]    # PC1 时间序列，shape: (T,)

# 如果 PC1 ≈ Beta 因子，它与等权组合收益的相关系数应 >0.9
corr = np.corrcoef(pc1_series, equal_weight)[0, 1]
```

若 q₁ 各资产载荷**全部同号** → 代表"所有资产同涨同跌"的系统性风险（Beta 因子）。今天实验中 SIM0050 载荷 ≈ -1，其余 ≈ 0，说明 PC1 被单一资产的大波动主导，非典型 Beta。

### 2.3 重构验证（数学完备性）

```python
Sigma_reconstructed = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T
max_error = np.abs(Sigma - Sigma_reconstructed).max()
# 实测误差 2.71e-19，接近 float64 机器精度（2.22e-16），完美
assert max_error < 1e-10
```

`np.diag(v)`：v 为一维数组时**生成对角矩阵**；v 为二维矩阵时**提取对角线**——两个方向功能相反，注意区分。

---

## 3. 整体学习进度与知识关联

- **复盘前序**：
  - Day 3：$\Sigma = \frac{R_c^T R_c}{T-1}$，构造协方差矩阵
  - Day 4：$\sigma_p^2 = w^T \Sigma w$，用 Σ 计算组合方差
  - **Day 5**：$\Sigma = Q \Lambda Q^T$，把 Σ 分解为"方向 × 强度"

- **当前里程碑**：打通了从数据 → 协方差矩阵 → 特征值分解 → 主成分因子的完整链路，理解了 PCA 降维的数学本质（正交旋转），以及第一主成分如何映射到金融中的市场 Beta 因子概念。

- **预告引申**：Day 6 用 NumPy Broadcasting 批量计算 252 个交易日的组合净值，不写一行 `for` 循环。

---

## 🔖 本日 API 速查

| API | 用途 | 关键参数/注意点 |
|-----|------|-----------------|
| `sla.eigh(A)` | 实对称矩阵特征值分解 | 返回升序特征值；比 `eig` 更快更稳定 |
| `arr[::-1]` | 一维数组翻转 | 步长 -1 |
| `arr[:, ::-1]` | 二维数组按列翻转 | 行不变，列倒序 |
| `np.diag(v)` | 一维→对角矩阵 / 二维→提取对角线 | 输入维度决定功能方向 |
| `np.cumsum(a)` | 累计求和 | `explained_ratio` 的累计解释率 |
| `np.corrcoef(x, y)` | Pearson 相关系数矩阵 | 返回 (2,2) 矩阵，取 `[0,1]` |

---

## 📌 掌握度标注（中）

需要继续巩固的点：
- **因子载荷的金融直觉**：什么情况是 Beta 因子、什么情况是行业因子，需结合真实数据再练一次
- **`np.corrcoef` 与二维矩阵**：传入 (T,N) 矩阵时的行为，避免维度混淆（见习题2改错）
