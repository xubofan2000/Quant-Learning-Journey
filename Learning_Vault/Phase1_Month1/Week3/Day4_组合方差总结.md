# Week 3 Day 4: 组合方差与风险度量 (w^T @ Σ @ w)

## 1. 核心认知与代码解释
今天我们将前面生成的协方差矩阵 `Σ` 投入实战，核心就是**马科维茨风险度量公式**测算组合的波动方差：
$$\sigma^2_p = w^T \Sigma w$$

在代码里表现为二次型乘法。这个基于理论推导（解析法）计算出的波动，被验证和纯历史面板序列（实证法）算出的波动等效完备：

```python
# 1. 解析法（马科维茨公式），利用 Day3 推导的 Sigma
step1 = Sigma @ w 
var_p = w @ step1  # 即 w.T @ Sigma @ w
sigma_p = np.sqrt(var_p)

# 2. 实证法（将历史日收益 R 乘权重 w，得到组合序列后再求标差）
portfolio_ret_series = R @ w  
sigma_p_historical = portfolio_ret_series.std(ddof=1)

# 两者计算完全吻合
assert np.isclose(sigma_p, sigma_p_historical)
```

## 2. 性能突破：降维打击 For 循环
为了刻画组合的风险-收益云图并试图寻找最优解，代码通过 `np.random.dirichlet` 暴力生成了 50,000 组满足 $w_i>0, \Sigma w_i=1$ 的权重。
在计算这 5 万个组合的方差时，代码展示了 NumPy 的矩阵化批处理技巧：

```python
W_all = np.random.dirichlet(np.ones(N), size=50000) # shape: (50000, 5)

# 🐌 传统 For 循环（龟速）：
for i in range(50000):
    vars_loop[i] = W_all[i] @ Sigma @ W_all[i]

# 🚀 降维批量运算（极致快，利用 BLAS 并行计算加速几十倍）：
WS = W_all @ Sigma                       # shape: (50000, 5)
vars_matrix = (WS * W_all).sum(axis=1)   # 将矩阵再乘一次权重而后逐行求和 -> (50000,)
```

## 3. 三种典型业务组合的对比
通过 Monte Carlo 云图扫描，代码中找出了三个锚点级别的经典模型，直接通过 Numpy API 即可定位：
*   等权组合：`w_equal = np.ones(N) / N`
*   MVP (最小方差组合)：`w_mvp = W_all[np.argmin(port_var)]`
*   最高夏普组合：`w_max_sharpe = W_all[np.argmax(port_sharpe)]`

## 4. 整体学习进度与知识关联
*   **复盘前序 (Day 1 - Day 3)：**
    *   我们在 Day 1-2 知道了 `W @ R.T` 是什么，这是获取组合时间收益序列。
    *   Day 3 徒手计算了协方差矩阵 `Σ = (R_c.T @ R_c) / (T-1)` 以捕捉所有资产的协方差/相关性，造出了可以全局量化并预测风险的标尺。
*   **当前里程碑 (Day 4)：**
    *   打通 “权重 $w$ -> 协方差矩阵 $\Sigma$ -> 组合方差极限度量 $\sigma^2$” 的死循环。今天就是这套底层的最终兵器测试，并且直接将矩阵乘法玩出花（性能优化）。
*   **预告引申 (接管 Week 4)：**
    *   今天我们在云图里大海捞针试出的 MVP 和 max Sharpe 其实都是“伪优解”（存在采样颗粒度制约且低效）。
    *   下周将引入**代数最优化 (scipy.optimize / 拉格朗日乘子)**，建立完整的带约束前沿模型：$\min w^T \Sigma w \quad s.t. \ w^T \mu \geq r_{\text{target}}$。从暴力穷举走向高阶解法。
