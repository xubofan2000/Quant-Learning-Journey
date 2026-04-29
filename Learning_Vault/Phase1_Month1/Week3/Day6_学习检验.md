# Day 6 学习检验：NumPy 广播机制与向量化回测

> 完成后请自评掌握度：**高 / 中 / 低**

---

## 🃏 Flashcards（概念速记）

**Q1**：`np.random.dirichlet(np.ones(N), size=M)` 生成的矩阵有什么特性？为什么它适合生成投资组合权重？

<details><summary>答案</summary>

生成 shape 为 `(M, N)` 的矩阵，**每一行元素非负且和为 1**。  
Dirichlet 分布天然满足全仓（满仓约束）和非空头（非负约束），无需额外的 `softmax` 或归一化步骤，是生成随机组合权重的标准方法。

</details>

---

**Q2**：`R @ W.T` 的金融含义是什么？为什么要对 W 做转置？

<details><summary>答案</summary>

- **金融含义**：同时计算 M 种策略在 T 天的每日组合收益率。结果第 `[t, m]` 个元素 = 第 `t` 天第 `m` 号策略的组合日收益。  
- **为什么转置**：`R` 是 `(T, N)`，`W` 是 `(M, N)`，矩阵乘法要求内维相同，所以 `W.T` 变为 `(N, M)`，结果为 `(T, M)`。

</details>

---

**Q3**：`np.cumprod(gross_returns, axis=0)` 中 `axis=0` 的含义？如果改成 `axis=1` 会计算什么？

<details><summary>答案</summary>

- `axis=0`：沿**时间轴**（行方向）做累乘 → 得到每个策略的资金净值曲线，这是我们想要的。  
- `axis=1`：沿**策略轴**（列方向）做累乘 → 对同一天内各策略收益连乘，无实际金融意义。

</details>

---

**Q4**：为什么 `gross_returns = 1 + returns_matrix` 这一行涉及到 Broadcasting？

<details><summary>答案</summary>

`1` 是标量（shape `()`），`returns_matrix` 是 `(T, M)` 的二维矩阵。  
NumPy 将标量自动广播到与矩阵相同的形状，等效于给矩阵每一个元素都加 1。这是 Broadcasting 最基础的形式：**标量 ↔ 任意维度张量**。

</details>

---

**Q5（金融业务直觉）**：随机生成 1 万种等权/随机权重策略后，期末净值的**均值**通常会小于等于大盘指数收益。为什么？

<details><summary>答案</summary>

随机权重策略的期望收益 ≈ 各股票等权平均收益，而大盘指数通常是**市值加权**（龙头股权重更高）。  
在 A 股，大盘龙头往往更稳定，因此市值加权指数可能优于随机等权平均。  
同时，随机组合中存在高集中度策略（重仓某只暴跌股），会拉低平均值。这也是为什么主动管理需要超越"随机猴子"基准。

</details>

---

## 💻 代码填空/改错题

### 题目 1：维度形状推演（Shape Intuition）

给定以下变量：
```python
T, N, M = 252, 50, 10_000
R = np.random.randn(T, N)   # 收益率矩阵
W = np.random.dirichlet(np.ones(N), size=M)  # 权重矩阵
```

填写每一步的输出 shape，并解释：

```python
step1 = W.T                    # shape: (____, ____)
step2 = R @ W.T                # shape: (____, ____)
step3 = 1 + step2              # shape: (____, ____)
step4 = np.cumprod(step3, axis=0)  # shape: (____, ____)
step5 = step4[-1, :]           # shape: (____)
best_idx = np.argmax(step5)    # shape: scalar，含义是？
```

<details><summary>答案</summary>

```
step1: (50, 10000)    # W 转置，N行M列
step2: (252, 10000)   # T天 × M个策略的每日收益
step3: (252, 10000)   # 标量Broadcasting，变为总收益因子
step4: (252, 10000)   # 每个策略的完整净值曲线
step5: (10000,)       # 所有策略的期末净值（一维）
best_idx: scalar      # 期末净值最大的策略编号（0-indexed）
```

</details>

---

### 题目 2：改错题

下面的代码想计算"最差策略的年化收益率"，找出其中的错误并修正：

```python
# 错误代码
worst_idx = np.argmax(final_navs)          # ← 错误1
annual_return = final_navs[worst_idx] * 100  # ← 错误2
print(f"最差策略年化收益: {annual_return:.2f}%")
```

<details><summary>答案</summary>

```python
# 修正后
worst_idx = np.argmin(final_navs)                    # 应用 argmin 找最小
annual_return = (final_navs[worst_idx] - 1) * 100    # NAV 减 1 才是收益率
print(f"最差策略年化收益: {annual_return:.2f}%")
```

两个错误：
1. `argmax` → `argmin`（找最差用最小值）
2. NAV 本身是净值（初始为1），需要 `-1` 后才是**收益率**，再乘 100 转为百分比

</details>

---

## 自评

完成以上题目后，请告诉我掌握度：**高 / 中 / 低**
