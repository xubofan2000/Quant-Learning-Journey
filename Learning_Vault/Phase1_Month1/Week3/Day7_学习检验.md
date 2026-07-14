# 📚 Week 3 Day 7 学习检验
# 模块封装 PortfolioMath 与 Week 3 大复盘
# 对应代码：day7_portfolio_math_module.py

---

## 🃏 闪卡（概念验证）

---

**Q1【编程】**：什么是 `@staticmethod`？为什么在这个 `PortfolioMath` 类中，所有的方法都要加上 `@staticmethod` 装饰器？

<details><summary>答案</summary>

`@staticmethod` 是 Python 中的静态方法装饰器。

**原因**：
`PortfolioMath` 是一个纯粹的“计算引擎”（工具类），它的方法只依赖于传入的参数（如收益率矩阵 `R`、权重向量 `w`），不需要保存或访问任何类实例的状态（不需要 `self`）。
加上 `@staticmethod` 后，可以直接通过类名调用，例如 `PortfolioMath.portfolio_variance(w, Sigma)`，无需先实例化对象（`p = PortfolioMath()`），这符合软件工程中“无状态纯函数”的最佳实践。

</details>

---

**Q2【编程】**：在类型注解 `def nav_curves(R: np.ndarray, W: np.ndarray) -> np.ndarray:` 中，`np.ndarray` 代表什么？加类型注解有什么好处？

<details><summary>答案</summary>

`np.ndarray` 代表 NumPy 的 N 维数组类型（N-dimensional array）。

**好处**：
1. **静态检查**：IDE（如 VS Code）会提供代码补全和类型警告，防止把 DataFrame 错传给需要 NumPy 数组的函数。
2. **增强可读性**：配合 docstring 使用，调用者一眼就能知道传入传出的是纯数学矩阵，而非其他对象。

</details>

---

**Q3【数学 / 编程】**：请回顾本周内容，将以下“金融公式”与对应的“NumPy 核心代码实现”连线对应：

1. 组合单日收益（内积）
2. 多天多策略批量组合收益
3. 协方差矩阵计算（无偏估计）
4. 马科维茨组合方差
5. 生成完整资金净值曲线

A. `np.cumprod(1 + R_matrix, axis=0)`
B. `w @ r`
C. `R @ W.T`
D. `(R_centered.T @ R_centered) / (T - 1)`
E. `w @ Sigma @ w`

<details><summary>答案</summary>

1 - B （`w @ r`）
2 - C （`R @ W.T`）
3 - D （`(R_centered.T @ R_centered) / (T - 1)`）
4 - E （`w @ Sigma @ w`）
5 - A （`np.cumprod(1 + R_matrix, axis=0)`）

</details>

---

**Q4【软件工程】**：为什么要将 `PortfolioMath` 单独抽离出来，而不是把数学计算和读取 Parquet 数据、过滤股票的代码写在同一个类里？

<details><summary>答案</summary>

这符合软件工程的 **“关注点分离”（Separation of Concerns）** 原则。

数据清洗模块（Pipeline）只管把脏数据处理成干净的矩阵 `R`；
数学模块（`PortfolioMath`）只管对矩阵进行纯粹的代数运算，它不关心数据是 Parquet 来的还是 API 抓取的。
解耦后，这个 `PortfolioMath` 类在 Phase 2 可以直接原封不动地拔插到 VectorBT 或其他回测框架中，复用性极高。

</details>

---

## 💻 代码习题

---

### 题目 1【形状推演 × 填空】

假设有一个调用端正在使用你的 `PortfolioMath` 工具：
已知有 $T=252$ 天的交易日，$N=50$ 只股票。你生成了 $M=10,000$ 种随机组合权重。

请推演以下各个变量的维度（Shape）：

```python
R = load_data()                     # R.shape: (_____, _____)
W = PortfolioMath.random_weights()  # W.shape: (_____, _____)

# 1. 批量收益矩阵
ret_mat = PortfolioMath.portfolio_returns_matrix(R, W)
# ret_mat.shape: (_____, _____)

# 2. 协方差矩阵与单策略方差
Sigma = PortfolioMath.covariance_matrix(R)
# Sigma.shape: (_____, _____)

w_single = W[0] # 取出第一种策略
var_p = PortfolioMath.portfolio_variance(w_single, Sigma)
# var_p 是一个 ________ (填数据类型，如 list, ndarray, float)
```

<details><summary>参考答案</summary>

```python
R = load_data()                     # R.shape: (252, 50)
W = PortfolioMath.random_weights()  # W.shape: (10000, 50)

# 1. 批量收益矩阵 (252, 50) @ (50, 10000) -> (252, 10000)
ret_mat = PortfolioMath.portfolio_returns_matrix(R, W)
# ret_mat.shape: (252, 10000)

# 2. 协方差矩阵与单策略方差
Sigma = PortfolioMath.covariance_matrix(R)
# Sigma.shape: (50, 50)

w_single = W[0] # 取出第一种策略 (50,)
var_p = PortfolioMath.portfolio_variance(w_single, Sigma)
# var_p 是一个 float (标量)
```

</details>

---

### 题目 2【代码审查（Code Review）】

以下是某位实习生向库里提交的一段代码，试图计算组合波动率。其中有两个不规范的地方，请指出：

```python
class JuniorMath:
    def portfolio_vol(self, w, Sigma, days=252):
        var = w.dot(Sigma).dot(w)
        if var < 0:
            var = 0
        return np.sqrt(var) * np.sqrt(days)

# 调用方代码
math_engine = JuniorMath()
math_engine.portfolio_vol(np.array([0.5, 0.5]), my_sigma)
```

<details><summary>答案</summary>

1. **未分离状态与方法设计不当**：方法不依赖实例状态 `self`，应该加上 `@staticmethod`。调用方每次还要 `math_engine = JuniorMath()` 实例化一遍，完全多此一举。
2. **缺乏类型注解与文档说明**：函数没有 `w: np.ndarray`, `Sigma: np.ndarray` 等类型提示（Type Hinting），也没有 Docstring 说明返回值是年化波动率，降低了框架的工程可靠性。
*(补充：虽然 `w.dot(Sigma).dot(w)` 语法正确，但现代 NumPy 更推荐 `w @ Sigma @ w` 增强公式可读性)*

</details>
