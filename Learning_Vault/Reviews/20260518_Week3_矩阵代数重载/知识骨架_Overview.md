# 🧠 Week 3 矩阵代数重载 (Warm-up Overview)

> 💡 **核心目标**：找回 NumPy 降维打击的手感，重新掌握从“单资产”到“多策略矩阵”的维度跃迁。

## 1. 维度形状速查表 (Shape Tracker)

在量化中，**维度不对，代码全废**。请时刻将以下变量维度刻在脑子里：

| 变量符号 | 业务含义 | 典型维度 (Shape) | 备注说明 |
| :--- | :--- | :--- | :--- |
| $N$ | 资产数量 (股票数) | 标量 (如 50) | 横截面维度 |
| $T$ | 时间周期 (交易日) | 标量 (如 252) | 时间序列维度 |
| $M$ | 策略数量 (组合数) | 标量 (如 10000) | 蒙特卡洛/并行测试维度 |
| $R$ | 收益率矩阵 | `(T, N)` | 每一行是一天的横截面收益 |
| $w$ | 单策略权重向量 | `(N,)` | 和为 1 |
| $W$ | 多策略权重矩阵 | `(M, N)` | 每一行代表一种策略的权重配置 |
| $\Sigma$ | 协方差矩阵 | `(N, N)` | 对称正半定矩阵 |

## 2. 核心数学与 NumPy API 映射

### ① 协方差矩阵推导 (Day 3)
*   **数学直觉**：每个资产减去自己的均值，然后自身转置相乘，除以自由度。
*   **公式**：$\Sigma = \frac{(R - \mu)^T (R - \mu)}{T - 1}$
*   **NumPy 实现**：
    ```python
    # 假设 R 是 (T, N)
    mu = R.mean(axis=0)             # (N,)
    R_centered = R - mu             # (T, N) - Broadcasting
    Sigma = (R_centered.T @ R_centered) / (T - 1)  # (N, N)
    ```

### ② 组合风险 (Portfolio Variance) (Day 4)
*   **数学直觉**：二次型映射。协方差矩阵被权重向量前后夹击，将 $N \times N$ 坍缩成一个标量（组合总风险）。
*   **公式**：$\sigma_p^2 = w^T \Sigma w$
*   **NumPy 实现**：`var_p = w @ Sigma @ w`

### ③ 市场因子提取 (PCA / 特征值分解) (Day 5)
*   **数学直觉**：把纠缠不清的协方差矩阵 $\Sigma$ 拆解为正交的特征向量（因子）和特征值（方差大小）。最大特征值对应的特征向量，通常代表市场系统性风险（Beta）。
*   **公式**：$\Sigma = Q \Lambda Q^T$
*   **NumPy API**：`scipy.linalg.eigh(Sigma)` （专门用于对称矩阵，返回按升序排列的特征值和特征向量）。
*   **方差解释率**：`lambda_1 / sum(lambdas)`

### ④ 万次策略并行回测 (Broadcasting) (Day 6)
*   **数学直觉**：彻底消灭 `for` 循环，用一次矩阵乘法算完 $M$ 个策略 $T$ 天的每日收益，再用累乘得到净值。
*   **公式**：$Returns\_Matrix = R W^T$
*   **NumPy 实现**：
    ```python
    returns_matrix = R @ W.T             # (T, N) @ (N, M) -> (T, M)
    nav_curves = np.cumprod(1 + returns_matrix, axis=0) # 沿时间轴累乘
    ```

---
**准备好了吗？请打开同目录下的 `恢复训练_Challenge.py`，开始手敲代码找回肌肉记忆吧！**
