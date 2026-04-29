# Week 3 Day 6: 广播机制与向量化回测 (NumPy Broadcasting & Vectorized Backtest)

> 掌握度自评：**中**

---

## 1. 核心认知与代码解释

### 今日核心：消灭循环，用矩阵乘法一次性完成 1 万个策略的回测

量化回测最大的性能陷阱就是嵌套 for 循环。对于"M 种策略 × T 个交易日"的计算，Python 原生循环会造成灾难级别的性能瓶颈。

**核心公式**：第 $t$ 天第 $m$ 个策略的组合收益 = $\sum_{i=1}^{N} R_{t,i} \cdot w_{m,i}$

用矩阵表示：

$$\text{returns\_matrix} = R \cdot W^T, \quad R \in \mathbb{R}^{T \times N},\; W \in \mathbb{R}^{M \times N}$$

结果 shape：$(T, N) \cdot (N, M) \rightarrow (T, M)$，**T 天 × M 个策略，一行搞定**。

```python
# 核心就是这五个字符
returns_matrix = R @ W.T   # (T, N) @ (N, M) -> (T, M)
```

性能对比（252天 × 1万策略）：
- 双重 for 循环：~数百 ms 至数秒
- 矩阵化：< 10 ms，**加速比通常 100x+**

---

## 2. 关键 API 速查

### 2.1 Dirichlet 分布生成权重

```python
W = np.random.dirichlet(np.ones(N), size=M)  # shape: (M, N)
# 每行元素非负且和为 1，天然满足满仓 + 无空头约束
```

> **为什么不用 softmax？** Dirichlet 分布直接生成，无需 normalization 步骤，且统计性质更均匀。

### 2.2 累积净值曲线

$$\text{NAV}_t = \prod_{k=1}^{t}(1 + R_k)$$

```python
gross_returns = 1 + returns_matrix   # Broadcasting: 标量 → (T, M)
nav_matrix = np.cumprod(gross_returns, axis=0)  # (T, M)，沿时间轴累乘
```

**`axis=0` 是时间轴**（沿行向下），`axis=1` 是策略轴（无金融意义）。

### 2.3 Broadcasting 核心规则

| 操作 | 形状变化 | 说明 |
|------|---------|------|
| `1 + (T, M)` | `(T, M)` | 标量广播到矩阵每个元素 |
| `R @ W.T` | `(T, N) @ (N, M) → (T, M)` | 矩阵乘法，内维消灭 |
| `nav[-1, :]` | `(T, M) → (M,)` | 取最后一行，提取期末净值 |

---

## 3. 维度形状推演（Shape Intuition）

```
T=252, N=50, M=10_000

W          (10000, 50)
W.T        (50, 10000)
R @ W.T    (252, 10000)   ← T天 × M策略的每日收益率
1 + R@W.T  (252, 10000)   ← 总收益因子（Broadcasting）
cumprod()  (252, 10000)   ← 每个策略的完整净值曲线
[-1, :]    (10000,)       ← 所有策略的期末净值
argmax()   scalar         ← 最优策略编号
```

---

## 4. 整体学习进度与知识关联

- **复盘前序**：
  - Day 1 的向量点乘 (`np.dot`) 是今天 `R @ W.T` 的基础——每个策略的每日收益本质就是一次向量点乘
  - Day 2 的矩阵乘法（`@` vs `*`）概念在今天得到了量化回测场景的完整应用
  - Day 4 的 $w^T \Sigma w$ 也是同一种"坍缩维度"的思路

- **当前里程碑**：打通了"向量化思维"在真实量化场景（多策略回测）的完整应用链路：生成权重 → 矩阵乘法计算收益 → Broadcasting 加 1 → cumprod 生成净值曲线 → argmax/argmin 筛选策略。

- **预告引申**：Week 3 Day 7 将进行综合收尾（Week 3 综合总结 / 练习）；下一阶段（Week 4）转向**概率统计与风险分布**，VaR、CVaR 等风险度量将基于今天的 `final_navs` 分布来计算。

---

## ⚠️ 中等掌握度 - 建议强化点

掌握度为"中"，以下知识点需要在后续复习时重点关注：

1. **Broadcasting 触发条件**：`1 + (T, M)` 是标量广播，是最简单的形式。中等掌握者往往在更复杂的 shape（如 `(T, 1)` 和 `(T, M)` 的广播）时容易出错——后续遇到时要画出维度对齐图。

2. **`axis` 参数的直觉**：`cumprod(axis=0)` 是沿时间轴，`axis=1` 是沿策略轴。建议记忆口诀：**axis=0 是纵向（时间/样本），axis=1 是横向（特征/策略）**。

3. **NAV 与收益率的换算**：`final_navs[i]` 是净值（初始=1），收益率 = `final_navs[i] - 1`。改错题中的经典坑——不减 1 直接乘 100 得到的是净值×100，不是百分比收益率。

---
*生成时间：2026-04-29*
