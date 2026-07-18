"""
Week 3 断点恢复训练：矩阵运算与 PortfolioMath

使用方法：
1. 在 VS Code 中按 # %% 单元格逐块运行。
2. 只填写标有 TODO 的位置，不先查看原 Day 7 代码。
3. 每完成一题，让对应 assert 通过后再进入下一题。
4. 全部通过后，再与 day7_portfolio_math_module.py 对照。
"""

# %% [0. 固定训练数据]
import sys

import numpy as np


sys.stdout.reconfigure(encoding="utf-8")


RETURNS = np.array(
    [
        [0.01, 0.00, -0.01],
        [0.02, -0.01, 0.00],
        [-0.01, 0.02, 0.01],
        [0.00, 0.01, 0.02],
    ],
    dtype=float,
)

WEIGHTS = np.array([0.5, 0.3, 0.2], dtype=float)
STRATEGY_WEIGHTS = np.array(
    [
        [0.5, 0.3, 0.2],
        [1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0],
    ],
    dtype=float,
)

TIME_COUNT, ASSET_COUNT = RETURNS.shape
STRATEGY_COUNT = STRATEGY_WEIGHTS.shape[0]

assert RETURNS.shape == (4, 3)
assert WEIGHTS.shape == (3,)
assert STRATEGY_WEIGHTS.shape == (3, 3)
print("✅ 训练数据已加载")


# %% [1. Shape 默写]
# TODO 1：只根据矩阵乘法规则填写三个 Shape，不运行矩阵试答案。
BATCH_RETURN_SHAPE = None
COVARIANCE_SHAPE = None
SINGLE_VARIANCE_TYPE = None

assert BATCH_RETURN_SHAPE == (TIME_COUNT, STRATEGY_COUNT), "R @ W.T 的 Shape 还不对"
assert COVARIANCE_SHAPE == (ASSET_COUNT, ASSET_COUNT), "协方差矩阵的 Shape 还不对"
assert SINGLE_VARIANCE_TYPE is float, "组合方差应当是 float 标量"
print("✅ Shape 直觉恢复")


# %% [2. 单组合每日收益]
def portfolio_returns(returns: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """计算一个组合在所有日期的收益，返回 shape (T,)。"""
    # TODO 2：检查资产维度与权重和，然后用一次矩阵乘法返回结果。
    raise NotImplementedError("请实现 portfolio_returns")


daily_returns = portfolio_returns(RETURNS, WEIGHTS)
expected_daily_returns = np.array([0.003, 0.007, 0.003, 0.007])

assert daily_returns.shape == (TIME_COUNT,)
assert np.allclose(daily_returns, expected_daily_returns)
print("✅ 单组合收益计算恢复")


# %% [3. 手写无偏协方差矩阵]
def covariance_matrix(returns: np.ndarray) -> np.ndarray:
    """按手推公式计算资产协方差矩阵，返回 shape (N, N)。"""
    # TODO 3：按资产列去均值，再用矩阵乘法和 T-1 计算无偏协方差。
    raise NotImplementedError("请实现 covariance_matrix")


sigma = covariance_matrix(RETURNS)
sigma_reference = np.cov(RETURNS, rowvar=False, ddof=1)

assert sigma.shape == (ASSET_COUNT, ASSET_COUNT)
assert np.allclose(sigma, sigma.T), "协方差矩阵必须对称"
assert np.allclose(sigma, sigma_reference), "手写结果应与 np.cov 一致"
print("✅ 协方差矩阵推导恢复")


# %% [4. 组合方差与年化波动率]
def portfolio_variance(weights: np.ndarray, sigma_matrix: np.ndarray) -> float:
    """使用马科维茨二次型计算组合方差。"""
    # TODO 4：检查维度，计算 w @ Sigma @ w，并返回 Python float。
    raise NotImplementedError("请实现 portfolio_variance")


def annualized_volatility(
    weights: np.ndarray,
    sigma_matrix: np.ndarray,
    trading_days: int = 252,
) -> float:
    """将日频组合方差转换为年化波动率。"""
    # TODO 5：复用 portfolio_variance，不要重复二次型公式。
    raise NotImplementedError("请实现 annualized_volatility")


variance = portfolio_variance(WEIGHTS, sigma)
volatility = annualized_volatility(WEIGHTS, sigma)

assert isinstance(variance, float)
assert np.isclose(variance, np.var(expected_daily_returns, ddof=1))
assert np.isclose(volatility, np.sqrt(variance) * np.sqrt(252))
print("✅ 组合风险计算恢复")


# %% [5. PCA / 特征值分解]
def eigendecomposition(sigma_matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """返回按降序排列的特征值，以及对应的列特征向量。"""
    # TODO 6：使用适合对称矩阵的 eigh，并把升序结果改为降序。
    raise NotImplementedError("请实现 eigendecomposition")


eigenvalues, eigenvectors = eigendecomposition(sigma)
reconstructed_sigma = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T

assert eigenvalues.shape == (ASSET_COUNT,)
assert eigenvectors.shape == (ASSET_COUNT, ASSET_COUNT)
assert np.all(np.diff(eigenvalues) <= 0), "特征值应按降序排列"
assert np.allclose(eigenvectors.T @ eigenvectors, np.eye(ASSET_COUNT))
assert np.allclose(reconstructed_sigma, sigma)
print("✅ PCA 数学验证恢复")


# %% [6. 多策略向量化收益与净值]
def batch_portfolio_returns(
    returns: np.ndarray,
    strategy_weights: np.ndarray,
) -> np.ndarray:
    """一次计算 M 个组合在 T 天的收益，返回 shape (T, M)。"""
    # TODO 7：不要写 for 循环，用矩阵乘法完成。
    raise NotImplementedError("请实现 batch_portfolio_returns")


def nav_curves(
    returns: np.ndarray,
    strategy_weights: np.ndarray,
) -> np.ndarray:
    """根据简单收益率生成每个组合的累计净值曲线。"""
    # TODO 8：复用 batch_portfolio_returns，沿时间轴累计连乘。
    raise NotImplementedError("请实现 nav_curves")


batch_returns = batch_portfolio_returns(RETURNS, STRATEGY_WEIGHTS)
expected_batch_returns = np.array(
    [
        [0.003, 0.01, -0.01],
        [0.007, 0.02, 0.00],
        [0.003, -0.01, 0.01],
        [0.007, 0.00, 0.02],
    ]
)
nav = nav_curves(RETURNS, STRATEGY_WEIGHTS)

assert batch_returns.shape == (TIME_COUNT, STRATEGY_COUNT)
assert np.allclose(batch_returns, expected_batch_returns)
assert nav.shape == (TIME_COUNT, STRATEGY_COUNT)
assert np.allclose(nav, np.cumprod(1 + expected_batch_returns, axis=0))
print("✅ 向量化回测恢复")


# %% [7. 封装为 PortfolioMath]
class PortfolioMath:
    """无状态的组合数学工具类。"""

    # TODO 9：把前面实现的函数作为静态方法挂到类上。
    # 提示：不需要重新复制函数体，可以直接使用 staticmethod(...)
    pass


required_methods = {
    "portfolio_returns",
    "covariance_matrix",
    "portfolio_variance",
    "annualized_volatility",
    "eigendecomposition",
    "batch_portfolio_returns",
    "nav_curves",
}
actual_methods = {
    name
    for name in dir(PortfolioMath)
    if not name.startswith("_")
}

assert required_methods.issubset(actual_methods), "PortfolioMath 还缺少静态方法"
assert np.allclose(PortfolioMath.portfolio_returns(RETURNS, WEIGHTS), expected_daily_returns)
assert np.allclose(PortfolioMath.nav_curves(RETURNS, STRATEGY_WEIGHTS), nav)
print("✅ PortfolioMath 模块封装恢复")


# %% [8. 完成提示]
print("\n🎉 所有断言通过：Week 3 矩阵运算与 PortfolioMath 手感已恢复！")
print("下一步：回看原 Day 7 模块，比较接口命名、输入检查和 docstring。")
