# Week 3 Day 5: 马科维茨优化求解 (scipy.optimize + SLSQP)

## 1. 核心认知跃迁：从暴力撒点到解析求解
Day 4 中我们通过 Monte Carlo 随机撒 50,000 个权重点来"大海捞针"式寻找最优组合，这种方法存在致命缺陷：
*   采样精度受限于随机数颗粒度，永远无法保证找到**真正的**最优解
*   计算效率低下，维度上升后指数爆炸

今天引入运筹学武器 `scipy.optimize.minimize`，将投资组合问题转化为一个**标准的带约束凸优化问题**：

| 要素 | 数学表达 | 代码实现 |
|------|---------|---------|
| **目标函数** | $\min \ w^T \Sigma_{ann} w$ | `port_variance(w)` |
| **等式约束** | $\sum w_i = 1$ (满仓) | `{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}` |
| **边界约束** | $0 \leq w_i \leq 1$ (做多) | `bounds = tuple((0, 1) for _ in range(N))` |
| **目标收益约束** (可选) | $w^T \mu \geq r_{target}$ | 追加等式约束锁定收益率 |

## 2. 两个关键求解目标

### 2.1 全局最小方差组合 (GMVP)
不关心收益，只找风险地板。目标函数直接就是 `port_variance(w)`：

```python
opt_gmvp = sco.minimize(
    port_variance,       # 最小化年化方差
    init_guess,          # 等权起点
    method='SLSQP',      # 序列最小二乘规划算法
    bounds=bounds,       # 0 <= w <= 1
    constraints=eq_cons  # sum(w) = 1
)
w_gmvp = opt_gmvp['x']  # 最优权重向量
```

### 2.2 最大夏普比率组合 (Tangency Portfolio)
核心技巧：**scipy 只有 minimize，没有 maximize**。所以对夏普比率取负号，最小化"负夏普"即是最大化夏普：

```python
def min_func_sharpe(w):
    """负夏普比率，minimize 它 = maximize 夏普"""
    return -(port_return(w) / port_volatility(w))

opt_sharpe = sco.minimize(min_func_sharpe, init_guess, method='SLSQP',
                          bounds=bounds, constraints=eq_cons)
```

与 Day 4 蒙特卡洛的 Sharpe ≈ 0.857 相比，优化器找到了**更精确的极值解**，揭示了数学梯度下降对随机搜索的绝对统治力。

## 3. 精确描绘有效前沿
Day 4 的有效前沿是从 50,000 个随机点中"筛出"的左侧边界，锯齿状且不连续。今天的做法是**参数化扫描**：

```python
# 在 GMVP 收益率和最大单资产收益率之间均匀取 30 个目标值
target_returns = np.linspace(port_return(w_gmvp), mu_ann.max(), 30)

for r_target in target_returns:
    constraints = (
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
        {'type': 'eq', 'fun': lambda x: port_return(x) - r_target}  # 锁定收益
    )
    res = sco.minimize(port_volatility, init_guess, method='SLSQP',
                       bounds=bounds, constraints=constraints)
    target_vols.append(res['fun'])
```

**逻辑**：把每个目标收益率作为新的等式约束注入优化器，强制求解该收益率下的最小波动率。30 个点串起来就是一条完美平滑的有效前沿弧线。

## 4. 技术要点备忘

| 概念 | 说明 |
|------|------|
| **SLSQP** | Sequential Least Squares Programming，带等式/不等式约束的非线性优化首选算法 |
| **等式约束** | `{'type': 'eq', 'fun': f}` → 要求 `f(x) = 0` |
| **不等式约束** | `{'type': 'ineq', 'fun': f}` → 要求 `f(x) >= 0` |
| **bounds** | 每个变量的上下界元组列表，用于框定搜索空间 |
| **init_guess** | 等权 `np.ones(N)/N` 作为优化起点，凸问题下起点不影响最终解 |
| **收敛检验** | `opt_result['success']` 和 `opt_result['fun']` 检查是否成功及目标值 |

## 5. 整体学习进度与知识关联

*   **复盘前序 (Day 1 → Day 4)：**
    *   Day 1-2：掌握向量/矩阵运算基础，`w @ R.T` 批量计算组合收益序列
    *   Day 3：徒手实现协方差矩阵 `Σ = (R_c.T @ R_c) / (T-1)`，捕捉全资产联动风险
    *   Day 4：`w.T @ Σ @ w` 组合方差公式实战，Monte Carlo 暴力搜索初步逼近最优组合
*   **当前里程碑 (Day 5)：**
    *   彻底完成从"暴力穷举"到"解析优化"的进化。用 `scipy.optimize` 精确定位 GMVP 和 Tangency Portfolio，用参数化约束扫描精确描绘有效前沿。Week 3 的矩阵代数 → 组合优化全链路打通。
*   **预告引申 (Week 4)：**
    *   Week 3 假设收益率服从正态分布（均值+协方差就够了）。但真实市场存在**尖峰厚尾、偏度**等非正态特征。Week 4 将引入概率统计工具，直面这些分布异常。
