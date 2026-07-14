"""
day7_portfolio_math_module.py - Week 3 Day 7: 模块封装 PortfolioMath

核心认知跃迁：
    本周我们一步步手写了量化组合数学的核心：
        Day 1: 向量点乘 → 组合单日收益
        Day 2: 矩阵乘法 → 多日多资产收益矩阵
        Day 3: 协方差矩阵 Σ
        Day 4: 组合方差 σ²_p = w^T Σ w
        Day 5: 特征值分解 Σ = Q Λ Qᵀ，PCA 市场因子
        Day 6: Broadcasting 向量化回测，1 行代码 × 1 万策略

    今天，我们把这些"散弹"代码凝结为一个专业的 Python 类：PortfolioMath。
    它是一个纯数学计算引擎（无状态、无副作用），
    可以被任何下游模块（未来的 VectorBT 封装、Phase 2 的因子回测框架）直接 import。

目标：
    1. 理解软件工程中"关注点分离"原则：数学逻辑 / 数据加载 / 可视化 各自独立
    2. 掌握 Python 类的设计：静态方法 (@staticmethod) vs 实例方法
    3. 用完整的 docstring 和类型注解使模块达到"生产可用"标准
    4. 用本周真实数据对每个方法进行端到端测试 (smoke test)
"""

# %% [0. 导入依赖]
import numpy as np
import pandas as pd
import os
from scipy import linalg

print("✅ 依赖库导入完成")

# %%  [1. 定义 PortfolioMath 类]
# 【编程概念】为何用 @staticmethod？
# 这些方法只依赖传入的参数（数组），不依赖任何实例状态（self.xxx）。
# @staticmethod 使调用方可以直接 PortfolioMath.method()，无需先实例化，
# 行为更像一个"函数命名空间"，这是工具类的惯用模式。

class PortfolioMath:
    """
    Week 3 量化组合数学工具类（纯计算引擎）

    所有方法均为 @staticmethod，直接通过类名调用：
        PortfolioMath.portfolio_return(w, r)
        PortfolioMath.covariance_matrix(R)
        ...

    数据约定（贯穿整个类）：
        N  : 资产数量
        T  : 时间周期（交易日数）
        M  : 策略数量（蒙特卡洛组合数）
        R  : 收益率矩阵，shape (T, N)，每行为一个交易日的各资产收益
        w  : 权重向量，shape (N,)，和为 1
        W  : 多策略权重矩阵，shape (M, N)，每行为一个策略的权重
        Σ  : 协方差矩阵，shape (N, N)
    """

    # ── Day 1 ────────────────────────────────────────────────────────────────
    @staticmethod
    def portfolio_return(w: np.ndarray, r: np.ndarray) -> float:
        """
        计算单个交易日的组合收益率（向量点乘）

        数学：r_p = w · r = Σ w_i * r_i

        Args:
            w: 权重向量，shape (N,)，应满足 sum=1
            r: 当日各资产收益向量，shape (N,)

        Returns:
            float: 当日组合收益率

        Example:
            w = np.array([0.3, 0.3, 0.4])
            r = np.array([0.01, -0.005, 0.02])
            PortfolioMath.portfolio_return(w, r)  # → 0.008
        """
        assert w.shape == r.shape, f"w.shape {w.shape} != r.shape {r.shape}"
        assert np.isclose(w.sum(), 1.0, atol=1e-6), f"权重之和不为1: {w.sum():.6f}"
        return float(w @ r)

    # ── Day 2 & 6 ────────────────────────────────────────────────────────────
    @staticmethod
    def portfolio_returns_matrix(R: np.ndarray, W: np.ndarray) -> np.ndarray:
        """
        向量化计算 M 种策略在 T 天的组合收益率矩阵（消灭 for 循环）

        数学：returns_matrix = R @ W.T
        维度：(T, N) @ (N, M) → (T, M)

        Args:
            R: 收益率矩阵，shape (T, N)
            W: 多策略权重矩阵，shape (M, N)，每行和为 1

        Returns:
            np.ndarray: shape (T, M)，第 [t, m] 元素为第 t 天第 m 个策略的组合收益
        """
        # 【数学概念】内维 N 消灭，外维 T×M 保留
        # 这是对 Day1 单次点乘的 M×T 次并行扩展，无 for 循环
        assert R.shape[1] == W.shape[1], \
            f"资产数不匹配: R.shape={R.shape}, W.shape={W.shape}"
        return R @ W.T  # (T, N) @ (N, M) → (T, M)

    # ── Day 3 ────────────────────────────────────────────────────────────────
    @staticmethod
    def covariance_matrix(R: np.ndarray) -> np.ndarray:
        """
        从收益率矩阵计算协方差矩阵 Σ（手推公式，等价于 np.cov）

        数学：Σ = (R - μ)ᵀ (R - μ) / (T - 1)
              其中 μ = R.mean(axis=0)，shape (N,)

        Args:
            R: 收益率矩阵，shape (T, N)

        Returns:
            np.ndarray: 对称正半定协方差矩阵，shape (N, N)
        """
        T, N = R.shape
        mu = R.mean(axis=0)          # 各资产均值，shape (N,)
        R_centered = R - mu          # 去均值，shape (T, N)  ← Broadcasting

        # 【数学概念】(T,N)ᵀ @ (T,N) = (N,T) @ (T,N) = (N,N)
        # 等价于 np.cov(R.T, ddof=1)，但手推更直观
        Sigma = (R_centered.T @ R_centered) / (T - 1)

        # 验证对称性（浮点误差范围内）
        assert np.allclose(Sigma, Sigma.T), "协方差矩阵不对称，数据异常"
        return Sigma

    # ── Day 4 ────────────────────────────────────────────────────────────────
    @staticmethod
    def portfolio_variance(w: np.ndarray, Sigma: np.ndarray) -> float:
        """
        计算组合方差（马科维茨二次型）

        数学：σ²_p = wᵀ Σ w

        Args:
            w: 权重向量，shape (N,)
            Sigma: 协方差矩阵，shape (N, N)

        Returns:
            float: 组合方差（年化前）
        """
        assert w.shape[0] == Sigma.shape[0] == Sigma.shape[1], \
            f"维度不匹配: w={w.shape}, Sigma={Sigma.shape}"
        var = float(w @ Sigma @ w)
        assert var >= -1e-10, f"组合方差为负 ({var:.2e})，Σ 可能不是半正定"
        return max(var, 0.0)  # 消除浮点误差导致的微小负值

    @staticmethod
    def portfolio_volatility(w: np.ndarray, Sigma: np.ndarray,
                             annualize: bool = True, trading_days: int = 252) -> float:
        """
        计算组合波动率（标准差），可选年化

        数学：σ_p = √(wᵀ Σ w)，年化 σ_p_annual = σ_p × √252

        Args:
            w: 权重向量，shape (N,)
            Sigma: 日频协方差矩阵，shape (N, N)
            annualize: 是否年化（默认 True）
            trading_days: 年交易日数（默认 252）

        Returns:
            float: 组合波动率（百分比形式请调用方 *100）
        """
        var = PortfolioMath.portfolio_variance(w, Sigma)
        vol = np.sqrt(var)
        return vol * np.sqrt(trading_days) if annualize else vol

    # ── Day 5 ────────────────────────────────────────────────────────────────
    @staticmethod
    def eigendecomposition(Sigma: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        对协方差矩阵进行特征值分解（eigh 专用于对称矩阵，更稳定）

        数学：Σ = Q Λ Qᵀ
              Q 的列是特征向量（主成分方向），Λ 的对角元素是特征值（方差）

        Args:
            Sigma: 对称正半定协方差矩阵，shape (N, N)

        Returns:
            eigenvalues:  shape (N,)，升序排列的特征值
            eigenvectors: shape (N, N)，列为对应特征向量
        """
        # 【编程概念】eigh 假设输入对称，比 eig 更快更精确，适合协方差矩阵
        eigenvalues, eigenvectors = linalg.eigh(Sigma)

        # eigh 返回升序，量化习惯降序（最大方差因子排第一）
        idx = np.argsort(eigenvalues)[::-1]
        return eigenvalues[idx], eigenvectors[:, idx]

    @staticmethod
    def variance_explained_ratio(eigenvalues: np.ndarray) -> np.ndarray:
        """
        计算每个主成分的方差解释率

        数学：ratio_k = λ_k / Σ λ_i

        Args:
            eigenvalues: 特征值数组，shape (N,)

        Returns:
            np.ndarray: 方差解释率，shape (N,)，和为 1
        """
        total = eigenvalues.sum()
        assert total > 0, "特征值之和为 0，协方差矩阵全零？"
        return eigenvalues / total

    # ── Day 6 ────────────────────────────────────────────────────────────────
    @staticmethod
    def nav_curves(R: np.ndarray, W: np.ndarray) -> np.ndarray:
        """
        生成 M 种策略的完整资金净值曲线（NAV）

        数学：NAV_t^(m) = ∏_{k=1}^{t} (1 + r_k^(m))

        Args:
            R: 收益率矩阵，shape (T, N)
            W: 多策略权重矩阵，shape (M, N)

        Returns:
            np.ndarray: NAV 矩阵，shape (T, M)，初始净值为 1
        """
        # 【数学概念】Broadcasting: 标量 1 + (T,M) → (T,M)
        # cumprod(axis=0): 沿时间轴累积乘积
        returns_matrix = PortfolioMath.portfolio_returns_matrix(R, W)
        gross_returns = 1 + returns_matrix
        return np.cumprod(gross_returns, axis=0)

    @staticmethod
    def random_weights(N: int, M: int, seed: int = None) -> np.ndarray:
        """
        生成 M 个随机满仓权重（Dirichlet 分布）

        Args:
            N: 资产数量
            M: 策略数量
            seed: 随机种子（可选，用于复现）

        Returns:
            np.ndarray: shape (M, N)，每行和为 1，元素非负
        """
        if seed is not None:
            np.random.seed(seed)
        # 【金融直觉】Dirichlet(1,...,1) = 均匀 Dirichlet，各权重服从均匀分布
        # 天然满足非负 + 满仓，无需 softmax 或 clip
        return np.random.dirichlet(np.ones(N), size=M)


print("✅ PortfolioMath 类定义完成")
print(f"   共 {len([m for m in dir(PortfolioMath) if not m.startswith('_')])} 个公开方法")

# %% [2. 加载真实数据]
# 【编程概念】动态路径定位，__file__ 是当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
parquet_path = os.path.join(project_root, 'Database', 'files', 'panel_50stocks.parquet')

df_panel = pd.read_parquet(parquet_path)
selected = df_panel['symbol'].unique()[:10]  # 取 10 只股票做 smoke test（更快）
N = len(selected)

df_w = df_panel[df_panel['symbol'].isin(selected)].pivot_table(
    index='trade_date', columns='symbol', values='daily_return'
).dropna().tail(252)

R = df_w.values   # shape (T, N)
T = R.shape[0]

print(f"\n📦 数据加载完成: R.shape = {R.shape}  # (T={T}, N={N})")

# %% [3. Smoke Test: portfolio_return]
# 验证单日点乘
w_equal = np.ones(N) / N   # 等权重
r_day0 = R[0]              # 第 1 天的收益率向量

r_p = PortfolioMath.portfolio_return(w_equal, r_day0)
r_p_manual = np.dot(w_equal, r_day0)

assert np.isclose(r_p, r_p_manual), "portfolio_return 验证失败"
print(f"\n✅ [Day1] portfolio_return:  等权组合第一天收益 = {r_p*100:+.4f}%")

# %% [4. Smoke Test: covariance_matrix]
Sigma = PortfolioMath.covariance_matrix(R)
Sigma_numpy = np.cov(R.T, ddof=1)

assert np.allclose(Sigma, Sigma_numpy, atol=1e-12), "covariance_matrix 与 np.cov 结果不一致"
print(f"\n✅ [Day3] covariance_matrix: Σ.shape = {Sigma.shape}, 与 np.cov 结果完全一致")

# %% [5. Smoke Test: portfolio_variance & volatility]
var_p = PortfolioMath.portfolio_variance(w_equal, Sigma)
vol_annual = PortfolioMath.portfolio_volatility(w_equal, Sigma, annualize=True)

print(f"\n✅ [Day4] portfolio_variance: 等权组合日频方差 = {var_p:.6f}")
print(f"         portfolio_volatility: 等权组合年化波动率 = {vol_annual*100:.2f}%")

# %% [6. Smoke Test: eigendecomposition]
eigenvalues, eigenvectors = PortfolioMath.eigendecomposition(Sigma)
ratios = PortfolioMath.variance_explained_ratio(eigenvalues)

# 验证重构误差（Σ ≈ Q Λ Qᵀ）
Q = eigenvectors
Lambda = np.diag(eigenvalues)
Sigma_reconstructed = Q @ Lambda @ Q.T
recon_error = np.max(np.abs(Sigma - Sigma_reconstructed))

print(f"\n✅ [Day5] eigendecomposition:")
print(f"         PC1 方差解释率 = {ratios[0]*100:.1f}%")
print(f"         重构误差 (max|Σ - QΛQᵀ|) = {recon_error:.2e}  ← 应接近机器精度")

# %% [7. Smoke Test: nav_curves & random_weights]
M = 1_000  # smoke test 用 1000 种策略，快一些
W = PortfolioMath.random_weights(N, M, seed=42)
nav = PortfolioMath.nav_curves(R, W)       # shape (T, M)
final_navs = nav[-1, :]                    # shape (M,)

best_return = (final_navs.max() - 1) * 100
mean_return = (final_navs.mean() - 1) * 100

print(f"\n✅ [Day6] nav_curves: nav.shape = {nav.shape}")
print(f"         1000 种随机策略一年期最优收益: {best_return:+.2f}%")
print(f"         1000 种随机策略一年期平均收益: {mean_return:+.2f}%")

# %% [8. 整合展示：一个完整的组合分析 Pipeline]
print("\n" + "=" * 55)
print("📐 PortfolioMath 完整 Pipeline 演示")
print("=" * 55)

# 步骤 1：构造等权权重
w_demo = np.ones(N) / N
print(f"\n[1] 等权权重 (N={N}): {np.round(w_demo, 3)}")

# 步骤 2：日频收益率序列
daily_returns = R @ w_demo   # shape (T,)
print(f"[2] 等权组合日频收益 shape: {daily_returns.shape}, 年化均值: {daily_returns.mean()*252*100:.2f}%")

# 步骤 3：协方差 + 组合方差
Sigma_demo = PortfolioMath.covariance_matrix(R)
vol_demo = PortfolioMath.portfolio_volatility(w_demo, Sigma_demo)
print(f"[3] 协方差矩阵: {Sigma_demo.shape}, 等权年化波动率: {vol_demo*100:.2f}%")

# 步骤 4：PCA
evals, evecs = PortfolioMath.eigendecomposition(Sigma_demo)
ratios_demo = PortfolioMath.variance_explained_ratio(evals)
print(f"[4] PC1 解释 {ratios_demo[0]*100:.1f}% 方差 (≈ 市场 Beta 因子)")

# 步骤 5：NAV 曲线（等权）
W_single = w_demo.reshape(1, N)   # shape (1, N)，单策略
nav_single = PortfolioMath.nav_curves(R, W_single)  # shape (T, 1)
total_return = (nav_single[-1, 0] - 1) * 100
print(f"[5] 等权策略一年期总收益: {total_return:+.2f}%")

print("\n✅ Day 7 完成！PortfolioMath 模块封装验证全部通过。")
print("   下一步: Week 4 概率统计与风险分布 (VaR / CVaR / 蒙特卡洛)")

# %%
